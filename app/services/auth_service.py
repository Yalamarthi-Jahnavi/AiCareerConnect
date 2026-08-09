"""
Authentication Service
========================
Business logic for user authentication (separate from route handlers).

WHY THIS FILE EXISTS:
    Keeps auth logic reusable and testable. Routes call this service
    instead of containing logic directly. If you change auth flow
    (e.g., add OAuth), only this file changes — not the routes.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from app.extensions import db
from app.models.user import User


class AuthService:
    """Handles authentication business logic."""
    
    @staticmethod
    def register_user(username, email, password, full_name='', role='job_seeker'):
        """
        Register a new user.
        
        Returns:
            tuple: (user_dict, tokens_dict) on success
            
        Raises:
            ValueError: If email or username already exists
        """
        if User.query.filter_by(email=email).first():
            raise ValueError('Email already registered')
        
        if User.query.filter_by(username=username).first():
            raise ValueError('Username already taken')
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        tokens = AuthService._generate_tokens(user.id)
        
        return user.to_dict(), tokens
    
    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate a user with email and password.
        
        Returns:
            tuple: (user_dict, tokens_dict) on success
            
        Raises:
            ValueError: If credentials are invalid
        """
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            raise ValueError('Invalid email or password')
        
        if not user.is_active:
            raise ValueError('Account is deactivated')
        
        tokens = AuthService._generate_tokens(user.id)
        
        return user.to_dict(), tokens
    
    @staticmethod
    def _generate_tokens(user_id):
        """Generate JWT access and refresh tokens."""
        return {
            'access_token': create_access_token(identity=str(user_id)),
            'refresh_token': create_refresh_token(identity=str(user_id)),
        }
