import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from backend.models import User

def generate_token(user_id):
    """
    Generate a JWT token for the given user_id.
    Reads expiry and algorithm from Flask app config.
    """
    exp_seconds = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 86400)
    algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=exp_seconds),
        'iat': datetime.datetime.utcnow(),
        'user_id': user_id
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm=algorithm)

def token_required(f):
    """
    Decorator to protect routes and inject the calling User object.
    Requires header: Authorization: Bearer <JWT_TOKEN>
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({"error": "Unauthorized", "message": "Authorization token is missing"}), 401
        
        try:
            # Decode token
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user:
                return jsonify({"error": "Unauthorized", "message": "User associated with token not found"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Unauthorized", "message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized", "message": "Token is invalid"}), 401
            
        return f(current_user, *args, **kwargs)
        
    return decorated
