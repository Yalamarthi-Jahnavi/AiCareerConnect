
"""
AI Career Connect - Application Factory

Creates and configures the Flask application using the
Application Factory Pattern.
"""

import os

from flask import Flask, render_template
from flask_cors import CORS

from app.config import config_by_name
from app.extensions import db, migrate, jwt


def create_app(config_name=None):
    """
    Application Factory.

    Configuration is selected using the FLASK_ENV environment
    variable. Production is used by default for deployment.
    """

    # Select configuration
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "production")

    # Safety fallback
    if config_name not in config_by_name:
        config_name = "production"

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    _initialize_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Enable CORS for frontend communication
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": "*"
            }
        }
    )

    # Base route
    @app.route("/")
    def index():
        return render_template("index.html")

    return app


def _initialize_extensions(app):
    """Initialize Flask extensions."""

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import models before creating database tables
    with app.app_context():
        from app.models import (
            user,
            job,
            application,
            resume
        )

        # Create database tables if they don't exist
        db.create_all()


def _register_blueprints(app):
    """Register all API route blueprints."""

    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.jobs import jobs_bp
    from app.routes.applications import applications_bp
    from app.routes.ai import ai_bp
    from app.routes.speech import speech_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    app.register_blueprint(
        users_bp,
        url_prefix="/api/users"
    )

    app.register_blueprint(
        jobs_bp,
        url_prefix="/api/jobs"
    )

    app.register_blueprint(
        applications_bp,
        url_prefix="/api/applications"
    )

    app.register_blueprint(
        ai_bp,
        url_prefix="/api/ai"
    )

    app.register_blueprint(
        speech_bp,
        url_prefix="/api/speech"
    )

    app.register_blueprint(
        dashboard_bp,
        url_prefix="/api/dashboard"
    )


def _register_error_handlers(app):
    """Register global error handlers."""

    @app.errorhandler(400)
    def bad_request(error):
        return {
            "success": False,
            "error": "Bad Request",
            "message": str(error)
        }, 400

    @app.errorhandler(404)
    def not_found(error):
        return {
            "success": False,
            "error": "Not Found",
            "message": "Resource not found"
        }, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {
            "success": False,
            "error": "Internal Server Error",
            "message": "Something went wrong"
        }, 500