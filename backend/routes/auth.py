from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import db, User, Profile
from backend.utils.security import generate_token, token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    
    email = data.get('email')
    password = data.get('password')
    role = data.get('role') # 'patient' or 'caregiver'
    full_name = data.get('full_name')
    phone_number = data.get('phone_number')
    language = data.get('language', 'en')
    
    if not email or not password or not role:
        return jsonify({"error": "Bad Request", "message": "Email, password, and role are required"}), 400
        
    if role not in ['patient', 'caregiver']:
        return jsonify({"error": "Bad Request", "message": "Role must be 'patient' or 'caregiver'"}), 400
        
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Conflict", "message": "Email is already registered"}), 409
        
    try:
        # Create User
        password_hash = generate_password_hash(password)
        new_user = User(email=email, password_hash=password_hash, role=role)
        db.session.add(new_user)
        db.session.flush() # Populate new_user.id
        
        # Create Profile
        new_profile = Profile(
            user_id=new_user.id,
            full_name=full_name,
            phone_number=phone_number,
            language=language
        )
        db.session.add(new_profile)
        db.session.commit()
        
        # Generate JWT Token
        token = generate_token(new_user.id)
        
        # Generate a simulated OTP for testing
        simulated_otp = current_app.config.get("MOCK_OTP_DEFAULT", "123456")
        
        return jsonify({
            "message": "Registration successful. OTP sent.",
            "token": token,
            "user": new_user.to_dict(),
            "profile": new_profile.to_dict(),
            "simulated_otp_sent": simulated_otp # Returning it in response for easy developer/client verification
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Bad Request", "message": "Email and password are required"}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Unauthorized", "message": "Invalid email or password"}), 401
        
    token = generate_token(user.id)
    profile = Profile.query.filter_by(user_id=user.id).first()
    
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict(),
        "profile": profile.to_dict() if profile else None
    }), 200

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """
    Mock OTP verification endpoint. Match against standard configured mock values.
    """
    data = request.get_json() or {}
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({"error": "Bad Request", "message": "Email and OTP code are required"}), 400
        
    expected_otp = current_app.config.get("MOCK_OTP_DEFAULT", "123456")
    
    if otp == expected_otp:
        return jsonify({
            "message": "OTP verification successful",
            "verified": True
        }), 200
    else:
        return jsonify({
            "error": "Unauthorized",
            "message": "Invalid OTP code",
            "verified": False
        }), 401

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Not Found", "message": "Profile not found"}), 404
        
    return jsonify({
        "user": current_user.to_dict(),
        "profile": profile.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        # Create one if missing
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
        
    data = request.get_json() or {}
    
    # Update fields if provided
    if 'full_name' in data:
        profile.full_name = data['full_name']
    if 'phone_number' in data:
        profile.phone_number = data['phone_number']
    if 'blood_type' in data:
        profile.blood_type = data['blood_type']
    if 'age' in data:
        profile.age = data['age']
    if 'height' in data:
        profile.height = data['height']
    if 'weight' in data:
        profile.weight = data['weight']
    if 'conditions' in data:
        profile.conditions = data['conditions']
    if 'allergies' in data:
        profile.allergies = data['allergies']
    if 'ec_name' in data:
        profile.ec_name = data['ec_name']
    if 'ec_rel' in data:
        profile.ec_rel = data['ec_rel']
    if 'ec_phone' in data:
        profile.ec_phone = data['ec_phone']
        
    try:
        db.session.commit()
        return jsonify({
            "message": "Profile updated successfully",
            "profile": profile.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
