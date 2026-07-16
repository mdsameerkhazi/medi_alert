from flask import Blueprint, jsonify
from backend.models import db, Notification
from backend.utils.security import token_required

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('', methods=['GET'])
@token_required
def get_notifications(current_user):
    """
    Retrieve notification history for the logged-in user, ordered by newest first.
    """
    try:
        notifs = Notification.query.filter_by(user_id=current_user.id).order_by(
            Notification.created_at.desc()
        ).all()
        return jsonify([n.to_dict() for n in notifs]), 200
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@notifications_bp.route('/<int:notif_id>/read', methods=['POST'])
@token_required
def mark_read(current_user, notif_id):
    """
    Mark a specific notification as read.
    """
    notif = Notification.query.get(notif_id)
    if not notif or notif.user_id != current_user.id:
        return jsonify({"error": "Not Found", "message": "Notification not found or unauthorized"}), 404
        
    try:
        notif.is_read = True
        db.session.commit()
        return jsonify(notif.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@notifications_bp.route('/clear-all', methods=['POST'])
@token_required
def clear_all(current_user):
    """
    Delete all notifications for the calling user.
    """
    try:
        Notification.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({"message": "All notifications cleared successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
