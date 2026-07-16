from flask import Blueprint, request, jsonify
from datetime import datetime
from backend.models import db, User, Profile, Medication, CaregiverRelation, VitalsLog
from backend.utils.security import token_required

health_bp = Blueprint('health', __name__)

@health_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    Get profile information.
    Patients get their own profile.
    Caregivers can pass ?patient_id= to fetch an authorized patient's profile,
    or omit it to get their own profile.
    """
    if current_user.role == 'caregiver':
        target_patient_id = request.args.get('patient_id')
        if target_patient_id:
            # Verify active caregiver relationship before fetching patient profile
            relation = CaregiverRelation.query.filter_by(
                patient_id=target_patient_id,
                caregiver_id=current_user.id,
                status='active'
            ).first()
            if not relation:
                return jsonify({"error": "Forbidden", "message": "Not authorized to view this patient"}), 403
            profile = Profile.query.filter_by(user_id=target_patient_id).first()
        else:
            # Caregiver fetching their own profile
            profile = Profile.query.filter_by(user_id=current_user.id).first()
    else:
        profile = Profile.query.filter_by(user_id=current_user.id).first()

    if not profile:
        return jsonify({"error": "Not Found", "message": "Profile not found"}), 404

    return jsonify(profile.to_dict()), 200


@health_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """
    Update calling user's own profile.
    Supports: full_name, phone_number, blood_type, emergency_contacts, primary_doctors, language.
    """
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Not Found", "message": "Profile not found"}), 404

    data = request.get_json() or {}
    allowed = ['full_name', 'phone_number', 'blood_type', 'emergency_contacts', 'primary_doctors', 'language']
    for field in allowed:
        if field in data:
            setattr(profile, field, data[field])

    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully", "profile": profile.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@health_bp.route('/medications', methods=['GET'])
@token_required
def get_medications(current_user):
    """
    Get medications list. Includes an optimized join to filter by patient.
    """
    patient_id = current_user.id
    
    if current_user.role == 'caregiver':
        target_patient_id = request.args.get('patient_id')
        if not target_patient_id:
            return jsonify({"error": "Bad Request", "message": "patient_id query parameter is required for caregivers"}), 400
            
        # Verify relation
        relation = CaregiverRelation.query.filter_by(
            patient_id=target_patient_id,
            caregiver_id=current_user.id,
            status='active'
        ).first()
        if not relation:
            return jsonify({"error": "Forbidden", "message": "You are not authorized to view this patient's medications"}), 403
        patient_id = target_patient_id

    # Optimized join: Fetch medications for patient
    meds = db.session.query(Medication).join(
        User, Medication.patient_id == User.id
    ).filter(User.id == patient_id).all()
    
    return jsonify([med.to_dict() for med in meds]), 200

@health_bp.route('/medications', methods=['POST'])
@token_required
def add_medication(current_user):
    """
    Add a new medication. Patients can add for themselves, caregivers can add for authorized patients.
    """
    data = request.get_json() or {}
    
    name = data.get('name')
    dosage = data.get('dosage')
    frequency = data.get('frequency')
    time_of_day = data.get('time_of_day')
    patient_id = data.get('patient_id', current_user.id)
    
    if not name or not dosage or not frequency or not time_of_day:
        return jsonify({"error": "Bad Request", "message": "name, dosage, frequency, and time_of_day are required"}), 400
        
    # Caregiver auth check
    if current_user.role == 'caregiver':
        relation = CaregiverRelation.query.filter_by(
            patient_id=patient_id,
            caregiver_id=current_user.id,
            status='active'
        ).first()
        if not relation:
            return jsonify({"error": "Forbidden", "message": "You are not authorized to add medications for this patient"}), 403
    elif int(patient_id) != current_user.id:
        return jsonify({"error": "Forbidden", "message": "You cannot add medications for another user"}), 403

    try:
        new_med = Medication(
            patient_id=patient_id,
            name=name,
            dosage=dosage,
            frequency=frequency,
            time_of_day=time_of_day,
            is_taken=False
        )
        db.session.add(new_med)
        db.session.commit()
        return jsonify(new_med.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@health_bp.route('/medications/<int:med_id>/log', methods=['POST'])
@token_required
def log_medication_taken(current_user, med_id):
    """
    Log a medication as taken (logs time and marks status).
    """
    med = Medication.query.get(med_id)
    if not med:
        return jsonify({"error": "Not Found", "message": "Medication not found"}), 404
        
    # Authorization checks
    if current_user.role == 'patient' and med.patient_id != current_user.id:
        return jsonify({"error": "Forbidden", "message": "You cannot update this medication status"}), 403
        
    if current_user.role == 'caregiver':
        relation = CaregiverRelation.query.filter_by(
            patient_id=med.patient_id,
            caregiver_id=current_user.id,
            status='active'
        ).first()
        if not relation:
            return jsonify({"error": "Forbidden", "message": "You are not authorized to log medication for this patient"}), 403

    try:
        med.is_taken = True
        med.last_taken_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            "message": "Medication logged successfully",
            "medication": med.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@health_bp.route('/vitals', methods=['POST'])
@token_required
def add_vitals(current_user):
    """
    Log today's vitals (heart_rate, bp_systolic, bp_diastolic, sleep_hours, steps).
    """
    if current_user.role != 'patient':
        return jsonify({"error": "Forbidden", "message": "Only patients can log vitals"}), 403
        
    data = request.get_json() or {}
    metric_type = data.get('metric_type')
    value = data.get('value')
    
    if not metric_type or value is None:
        return jsonify({"error": "Bad Request", "message": "metric_type and value are required"}), 400
        
    if metric_type not in ['heart_rate', 'bp_systolic', 'bp_diastolic', 'sleep_hours', 'steps']:
        return jsonify({"error": "Bad Request", "message": "Invalid metric_type"}), 400
        
    try:
        log = VitalsLog(
            patient_id=current_user.id,
            metric_type=metric_type,
            value=float(value)
        )
        db.session.add(log)
        db.session.commit()
        return jsonify(log.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@health_bp.route('/vitals', methods=['GET'])
@token_required
def get_vitals(current_user):
    """
    Fetch vitals history. Caregivers can query for authorized patients.
    """
    patient_id = current_user.id
    if current_user.role == 'caregiver':
        target_patient_id = request.args.get('patient_id')
        if not target_patient_id:
            return jsonify({"error": "Bad Request", "message": "patient_id query parameter is required for caregivers"}), 400
        # Verify relationship
        relation = CaregiverRelation.query.filter_by(
            patient_id=target_patient_id,
            caregiver_id=current_user.id,
            status='active'
        ).first()
        if not relation:
            return jsonify({"error": "Forbidden", "message": "Unauthorized patient access"}), 403
        patient_id = target_patient_id
        
    metric_type = request.args.get('metric_type')
    
    query = VitalsLog.query.filter_by(patient_id=patient_id)
    if metric_type:
        query = query.filter_by(metric_type=metric_type)
        
    logs = query.order_by(VitalsLog.timestamp.desc()).limit(50).all()
    return jsonify([log.to_dict() for log in logs]), 200
