"""
AI Career Connect - Flask Extensions
======================================
Centralized initialization of all Flask extensions.

WHY THIS FILE EXISTS:
    Extensions are created here WITHOUT an app instance (lazy initialization).
    This avoids circular imports — models and routes can import 'db' or 'jwt'
    from here without needing the app object. The app factory calls
    ext.init_app(app) later to bind them.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Database ORM
db = SQLAlchemy()

# Database migrations (Alembic)
migrate = Migrate()

# JWT Authentication
jwt = JWTManager()
