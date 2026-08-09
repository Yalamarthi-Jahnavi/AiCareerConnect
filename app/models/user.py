"""
User Model
===========
Represents users of the platform (job seekers, employers, admins).

WHY THIS FILE EXISTS:
    Separating each model into its own file keeps things organized.
    The User model is the core of authentication and profile management.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    """User account for the AI Career Connect platform."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profile Information
    full_name = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)  # Comma-separated skills
    experience_years = db.Column(db.Integer, default=0)
    
    # Role: 'job_seeker', 'employer', 'admin'
    role = db.Column(db.String(20), default='job_seeker', nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='applicant', lazy='dynamic')
    resumes = db.relationship('Resume', backref='owner', lazy='dynamic')
    posted_jobs = db.relationship('Job', backref='employer', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and store the password securely."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Serialize user to dictionary (excludes password)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'location': self.location,
            'bio': self.bio,
            'skills': self.skills.split(',') if self.skills else [],
            'experience_years': self.experience_years,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
