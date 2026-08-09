"""
Resume Model
==============
Represents an uploaded resume and its AI-parsed data.

WHY THIS FILE EXISTS:
    Resumes are uploaded as files but also need structured data extracted
    from them (skills, experience, education). The AI service parses the
    file and stores structured results here for fast querying.
"""

from datetime import datetime
from app.extensions import db


class Resume(db.Model):
    """Resume uploaded by a job seeker with AI-extracted data."""
    
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # File Information
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)  # bytes
    
    # AI-Extracted Data (populated by Mistral AI)
    extracted_text = db.Column(db.Text, nullable=True)       # Raw text from resume
    extracted_skills = db.Column(db.Text, nullable=True)      # Comma-separated skills
    extracted_experience = db.Column(db.Text, nullable=True)  # JSON string of experience
    extracted_education = db.Column(db.Text, nullable=True)   # JSON string of education
    ai_summary = db.Column(db.Text, nullable=True)            # AI-generated summary
    
    # Metadata
    is_primary = db.Column(db.Boolean, default=False)  # User's primary resume
    is_parsed = db.Column(db.Boolean, default=False)   # Has AI processed it?
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    parsed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    applications = db.relationship('Application', backref='resume', lazy='dynamic')
    
    def to_dict(self):
        """Serialize resume to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'file_size': self.file_size,
            'extracted_skills': self.extracted_skills.split(',') if self.extracted_skills else [],
            'ai_summary': self.ai_summary,
            'is_primary': self.is_primary,
            'is_parsed': self.is_parsed,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
    
    def __repr__(self):
        return f'<Resume {self.filename} by User:{self.user_id}>'
