from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.models import db
from backend.routes.auth import auth_bp
from backend.routes.health import health_bp
from backend.routes.emergency import emergency_bp
from backend.routes.caregiver import caregiver_bp
from backend.routes.notifications import notifications_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable Cross-Origin Resource Sharing
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(emergency_bp, url_prefix='/api/emergency')
    app.register_blueprint(caregiver_bp, url_prefix='/api/caregiver')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    
    # Custom Error Handlers
    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify({
            "error": "Not Found",
            "message": "The requested API endpoint does not exist"
        }), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred on the server"
        }), 500
        
    # Auto-create tables (useful for fast-track MVP deployment)
    try:
        with app.app_context():
            db.create_all()
    except Exception as err:
        print(f"Warning: Could not create tables on startup. Check DB connection details. Error: {err}")
        
    return app

if __name__ == '__main__':
    app = create_app()
    # Runs on port 5000 by default for backend APIs
    app.run(host='0.0.0.0', port=5000, debug=True)
