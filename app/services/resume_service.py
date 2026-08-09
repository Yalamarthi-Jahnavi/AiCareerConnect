"""
Resume Service
================
Handles resume upload, text extraction, and processing.

WHY THIS FILE EXISTS:
    Resume processing involves file handling, text extraction from PDFs,
    and AI analysis. This complex logic is kept separate from routes
    to maintain clean architecture.
"""

import os
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.resume import Resume


class ResumeService:
    """Handles resume upload and processing logic."""
    
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    
    @staticmethod
    def allowed_file(filename):
        """Check if the file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ResumeService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def save_resume(user_id, file):
        """
        Save an uploaded resume file and create a database record.
        
        Args:
            user_id: ID of the user uploading
            file: FileStorage object from request.files
            
        Returns:
            Resume: The created Resume model instance
        """
        if not file or not ResumeService.allowed_file(file.filename):
            raise ValueError('Invalid file. Allowed types: PDF, DOC, DOCX, TXT')
        
        # Secure the filename and save
        filename = secure_filename(file.filename)
        upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        user_dir = os.path.join(upload_dir, str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        
        filepath = os.path.join(user_dir, filename)
        file.save(filepath)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Create database record
        resume = Resume(
            user_id=user_id,
            filename=filename,
            file_path=filepath,
            file_size=file_size,
        )
        
        db.session.add(resume)
        db.session.commit()
        
        # Extract text from the resume
        extracted_text = ResumeService.extract_text(filepath)
        if extracted_text:
            resume.extracted_text = extracted_text
            resume.is_parsed = True
            resume.parsed_at = datetime.utcnow()
            db.session.commit()
        
        return resume
    
    @staticmethod
    def extract_text(filepath):
        """
        Extract text content from a resume file.
        
        Supports: TXT, PDF (with PyPDF2), DOCX (with python-docx)
        """
        extension = filepath.rsplit('.', 1)[1].lower()
        
        try:
            if extension == 'txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif extension == 'pdf':
                try:
                    import PyPDF2
                    with open(filepath, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ''
                        for page in reader.pages:
                            text += page.extract_text() or ''
                        return text
                except ImportError:
                    return None  # PyPDF2 not installed
            
            elif extension in ('doc', 'docx'):
                try:
                    import docx
                    doc = docx.Document(filepath)
                    return '\n'.join([para.text for para in doc.paragraphs])
                except ImportError:
                    return None  # python-docx not installed
            
        except Exception as e:
            print(f'Error extracting text from {filepath}: {e}')
            return None
        
        return None
    
    @staticmethod
    def set_primary_resume(user_id, resume_id):
        """Set a resume as the user's primary resume."""
        # Unset all current primary resumes
        Resume.query.filter_by(user_id=user_id, is_primary=True)\
            .update({'is_primary': False})
        
        # Set the new primary
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            raise ValueError('Resume not found')
        
        resume.is_primary = True
        db.session.commit()
        
        return resume
