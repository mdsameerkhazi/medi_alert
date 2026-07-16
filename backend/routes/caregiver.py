from flask import Blueprint, request, jsonify
from backend.models import db, User, Profile, CaregiverInvitation, CaregiverRelation, Notification
from backend.utils.security import token_required

caregiver_bp = Blueprint('caregiver', __name__)

@caregiver_bp.route('/invite', methods=['POST'])
@token_required
def send_invite(current_user):
    """
    Send an invitation to connect. Sender is current user, receiver is specified by email.
    Creates a notification for the receiver.
    """
    data = request.get_json() or {}
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Bad Request", "message": "Email is required"}), 400
        
    # Find receiver user
    receiver = User.query.filter_by(email=email).first()
    if not receiver:
        return jsonify({"error": "Not Found", "message": "User with this email not found"}), 404
        
    if receiver.id == current_user.id:
        return jsonify({"error": "Bad Request", "message": "You cannot invite yourself"}), 400
        
    if receiver.role == current_user.role:
        return jsonify({"error": "Conflict", "message": f"Both users are {current_user.role}s. A link must be between a Patient and a Caregiver."}), 400
        
    # Prevent duplicate pending invitations
    existing_invite = CaregiverInvitation.query.filter_by(
        sender_id=current_user.id,
        receiver_email=email,
        status='pending'
    ).first()
    if existing_invite:
        return jsonify({"error": "Conflict", "message": "An invitation to this email is already pending"}), 409

    try:
        # Create invitation
        invite = CaregiverInvitation(
            sender_id=current_user.id,
            receiver_email=email,
            status='pending'
        )
        db.session.add(invite)
        db.session.flush()
        
        # Create a notification for the receiver
        sender_profile = Profile.query.filter_by(user_id=current_user.id).first()
        sender_name = sender_profile.full_name if sender_profile and sender_profile.full_name else current_user.email
        
        notif = Notification(
            user_id=receiver.id,
            title="Connection Request",
            message=f"{sender_name} ({current_user.role}) has invited you to connect.",
            is_read=False
        )
        db.session.add(notif)
        db.session.commit()
        
        return jsonify(invite.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@caregiver_bp.route('/invitations', methods=['GET'])
@token_required
def list_invitations(current_user):
    """
    List pending incoming invitations for the calling user.
    """
    # Fetch invitations where receiver_email matches calling user's email
    results = db.session.query(CaregiverInvitation, Profile.full_name, User.role).join(
        User, CaregiverInvitation.sender_id == User.id
    ).join(
        Profile, User.id == Profile.user_id
    ).filter(
        CaregiverInvitation.receiver_email == current_user.email,
        CaregiverInvitation.status == 'pending'
    ).all()
    
    invitations_list = []
    for invite, sender_name, sender_role in results:
        data = invite.to_dict()
        data['sender_name'] = sender_name
        data['sender_role'] = sender_role
        invitations_list.append(data)
        
    return jsonify(invitations_list), 200

@caregiver_bp.route('/invitations/<int:invite_id>/respond', methods=['POST'])
@token_required
def respond_invite(current_user, invite_id):
    """
    Respond to a pending incoming invitation (accept / reject).
    If accepted, automatically creates a CaregiverRelation.
    """
    data = request.get_json() or {}
    action = data.get('action') # 'accept' or 'reject'
    
    if action not in ['accept', 'reject']:
        return jsonify({"error": "Bad Request", "message": "Action must be 'accept' or 'reject'"}), 400
        
    invite = CaregiverInvitation.query.get(invite_id)
    if not invite or invite.receiver_email != current_user.email:
        return jsonify({"error": "Not Found", "message": "Invitation not found or unauthorized"}), 404
        
    if invite.status != 'pending':
        return jsonify({"error": "Conflict", "message": "Invitation has already been processed"}), 409
        
    try:
        invite.status = 'accepted' if action == 'accept' else 'rejected'
        
        if action == 'accept':
            # Create caregiver relation. Determine who is who.
            sender = User.query.get(invite.sender_id)
            if not sender:
                return jsonify({"error": "Conflict", "message": "Sender user no longer exists"}), 400
                
            if current_user.role == 'caregiver' and sender.role == 'patient':
                patient_id = sender.id
                caregiver_id = current_user.id
            elif current_user.role == 'patient' and sender.role == 'caregiver':
                patient_id = current_user.id
                caregiver_id = sender.id
            else:
                return jsonify({"error": "Conflict", "message": "Invalid linkage roles (must link a Patient to a Caregiver)"}), 400
                
            # Verify if duplicate relation exists
            existing_relation = CaregiverRelation.query.filter_by(
                patient_id=patient_id,
                caregiver_id=caregiver_id
            ).first()
            
            if not existing_relation:
                relation = CaregiverRelation(
                    patient_id=patient_id,
                    caregiver_id=caregiver_id,
                    status='active'
                )
                db.session.add(relation)
                
            # Notify the sender that the request was accepted
            notif = Notification(
                user_id=invite.sender_id,
                title="Invitation Accepted",
                message=f"{current_user.email} has accepted your caregiver linkage invitation.",
                is_read=False
            )
            db.session.add(notif)

        db.session.commit()
        return jsonify({
            "message": f"Invitation {action}ed successfully",
            "invitation": invite.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
