"""
Application Model
==================
Represents a job application submitted by a job seeker.

WHY THIS FILE EXISTS:
    This is the many-to-many bridge between Users and Jobs.
    It tracks the full lifecycle of an application: applied → reviewed
    → interview → offered → hired/rejected.
"""

from datetime import datetime
from app.extensions import db


class Application(db.Model):
    """Job application linking a user to a job listing."""
    
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=True)
    
    # Application Details
    cover_letter = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='applied')
    # Statuses: applied, reviewed, shortlisted, interview, offered, hired, rejected, withdrawn
    
    # AI Match Score (calculated by Mistral AI)
    match_score = db.Column(db.Float, nullable=True)  # 0.0 to 100.0
    ai_feedback = db.Column(db.Text, nullable=True)   # AI-generated feedback
    
    # Timestamps
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Prevent duplicate applications
    __table_args__ = (
        db.UniqueConstraint('user_id', 'job_id', name='unique_user_job_application'),
    )
    
    def to_dict(self):
        """Serialize application to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'resume_id': self.resume_id,
            'cover_letter': self.cover_letter,
            'status': self.status,
            'match_score': self.match_score,
            'ai_feedback': self.ai_feedback,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<Application User:{self.user_id} → Job:{self.job_id} [{self.status}]>'
