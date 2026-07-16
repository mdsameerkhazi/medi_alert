from flask import Blueprint, request, jsonify
from backend.models import db, SOSAlert, CaregiverRelation, Profile
from backend.utils.security import token_required

emergency_bp = Blueprint('emergency', __name__)

@emergency_bp.route('/trigger-sos', methods=['POST'])
@token_required
def trigger_sos(current_user):
    """
    Trigger an emergency SOS. Saves location and flags active state.
    Simulates caregiver notification.
    """
    if current_user.role != 'patient':
        return jsonify({"error": "Forbidden", "message": "Only patients can trigger SOS alerts"}), 403
        
    data = request.get_json() or {}
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if latitude is None or longitude is None:
        return jsonify({"error": "Bad Request", "message": "latitude and longitude are required"}), 400
        
    try:
        # Create the alert
        alert = SOSAlert(
            patient_id=current_user.id,
            latitude=float(latitude),
            longitude=float(longitude),
            status='active'
        )
        db.session.add(alert)
        db.session.commit()
        
        # Optimized query to fetch names of notified caregivers to return in metadata
        caregivers = db.session.query(Profile.full_name).join(
            CaregiverRelation, CaregiverRelation.caregiver_id == Profile.user_id
        ).filter(
            CaregiverRelation.patient_id == current_user.id,
            CaregiverRelation.status == 'active'
        ).all()
        
        caregiver_names = [c[0] for c in caregivers]
        
        return jsonify({
            "message": "SOS Alert triggered successfully. SMS notifications simulated to caregivers.",
            "alert": alert.to_dict(),
            "notified_caregivers": caregiver_names
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@emergency_bp.route('/caregiver-alerts', methods=['GET'])
@token_required
def get_caregiver_alerts(current_user):
    """
    Get active alerts for patients connected to this caregiver.
    Uses optimized joins across SOSAlerts, CaregiverRelations, and Profiles.
    """
    if current_user.role != 'caregiver':
        return jsonify({"error": "Forbidden", "message": "Only caregivers can fetch caregiver alerts"}), 403
        
    try:
        # Complex join matching caregiver relations with active patient alerts and resolving patient names
        results = db.session.query(SOSAlert, Profile.full_name, Profile.phone_number).join(
            CaregiverRelation, SOSAlert.patient_id == CaregiverRelation.patient_id
        ).join(
            Profile, SOSAlert.patient_id == Profile.user_id
        ).filter(
            CaregiverRelation.caregiver_id == current_user.id,
            CaregiverRelation.status == 'active',
            SOSAlert.status == 'active'
        ).order_by(SOSAlert.triggered_at.desc()).all()
        
        alerts_list = []
        for alert, patient_name, patient_phone in results:
            alert_data = alert.to_dict()
            alert_data['patient_name'] = patient_name
            alert_data['patient_phone'] = patient_phone
            alerts_list.append(alert_data)
            
        return jsonify(alerts_list), 200
        
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
