from flask import Flask, render_template, jsonify
from app.config import Config
from app.models import db
from app.logger import setup_logging
from app.metrics import register_metrics

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    setup_logging(app)
    register_metrics(app)

    # Register blueprints
    from app.routes.web import web_bp
    from app.routes.api import api_bp
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import request
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Resource not found", "status_code": 404}), 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import request
        db.session.rollback()
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Internal server error", "status_code": 500}), 500
        return render_template("500.html"), 500

    return app
