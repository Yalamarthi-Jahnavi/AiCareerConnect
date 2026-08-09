"""
Job Model
==========
Represents a job listing posted by an employer.

WHY THIS FILE EXISTS:
    Job listings are the core content of the platform. This model
    stores all job details and links back to the employer who posted it.
"""

from datetime import datetime
from app.extensions import db


class Job(db.Model):
    """Job listing on the AI Career Connect platform."""
    
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    company = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Job Details
    location = db.Column(db.String(100), nullable=True)
    job_type = db.Column(db.String(50), default='full-time')  # full-time, part-time, contract, remote
    salary_min = db.Column(db.Float, nullable=True)
    salary_max = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default='INR')
    
    # Skills & Requirements
    required_skills = db.Column(db.Text, nullable=True)  # Comma-separated
    experience_required = db.Column(db.Integer, default=0)  # Years
    education_level = db.Column(db.String(50), nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, closed, draft
    is_featured = db.Column(db.Boolean, default=False)
    
    # Foreign Key - who posted this job
    employer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    applications = db.relationship('Application', backref='job', lazy='dynamic')
    
    def to_dict(self):
        """Serialize job to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'location': self.location,
            'job_type': self.job_type,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'currency': self.currency,
            'required_skills': self.required_skills.split(',') if self.required_skills else [],
            'experience_required': self.experience_required,
            'education_level': self.education_level,
            'status': self.status,
            'is_featured': self.is_featured,
            'employer_id': self.employer_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'application_count': self.applications.count(),
        }
    
    def __repr__(self):
        return f'<Job {self.title} at {self.company}>'
