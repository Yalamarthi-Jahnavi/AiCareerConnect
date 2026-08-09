"""
AI Routes (Mistral API Integration)
=====================================
AI-powered endpoints for resume analysis, job matching, and career advice.

WHY THIS FILE EXISTS:
    All AI/Mistral-powered features are grouped here. This keeps AI logic
    separate from standard CRUD operations. Routes call the ai_service
    for actual Mistral API communication.
    
Endpoints:
    POST /api/ai/analyze-resume      - AI-analyze an uploaded resume
    POST /api/ai/match-jobs          - Get AI job recommendations for a user
    POST /api/ai/career-advice       - Get AI career guidance
    POST /api/ai/improve-resume      - Get AI suggestions to improve resume
    POST /api/ai/interview-prep      - Generate AI interview questions
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.services.ai_service import MistralAIService

# Create Blueprint
ai_bp = Blueprint('ai', __name__)

# Initialize AI service
ai_service = MistralAIService()


# ============================================================
# ANALYZE RESUME
# ============================================================

@ai_bp.route('/analyze-resume', methods=['POST'])
@jwt_required()
def analyze_resume():
    """Analyze a resume using Mistral AI and extract structured data."""
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    
    resume_id = data.get('resume_id')
    if not resume_id:
        return jsonify({'success': False, 'message': 'resume_id is required'}), 400
    
    try:
        user_id = int(user_id)
        resume_id = int(resume_id)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid user_id or resume_id'}), 400
    
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
    if not resume:
        return jsonify({'success': False, 'message': 'Resume not found'}), 404
    
    if not resume.extracted_text:
        return jsonify({'success': False, 'message': 'Resume text not yet extracted. Upload the resume first.'}), 400
    
    try:
        analysis = ai_service.analyze_resume(resume.extracted_text)
        return jsonify({'success': True, 'analysis': analysis}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'AI analysis failed: {str(e)}'}), 500


# ============================================================
# MATCH JOBS
# ============================================================

@ai_bp.route('/match-jobs', methods=['POST'])
@jwt_required()
def match_jobs():
    """Get AI-powered job recommendations based on user profile/resume."""
    user_id = get_jwt_identity()
    
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid user ID'}), 400
    
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Get user's primary/latest resume
    resume = Resume.query.filter_by(user_id=user.id, is_primary=True).first()
    
    # Get active jobs
    active_jobs = Job.query.filter_by(status='active').limit(50).all()
    jobs_data = [job.to_dict() for job in active_jobs]
    
    try:
        user_profile = {
            'skills': user.skills,
            'experience_years': user.experience_years,
            'location': user.location,
            'bio': user.bio,
            'resume_summary': resume.ai_summary if resume else None,
        }
        
        matches = ai_service.match_jobs(user_profile, jobs_data)
        return jsonify({'success': True, 'matches': matches}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Job matching failed: {str(e)}'}), 500


# ============================================================
# CAREER ADVICE
# ============================================================

@ai_bp.route('/career-advice', methods=['POST'])
@jwt_required()
def career_advice():
    """Get personalized AI career advice."""
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    
    question = data.get('question', '').strip()
    if not question:
        return jsonify({'success': False, 'message': 'question is required'}), 400
    
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid user ID'}), 400
    
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    try:
        context = {
            'skills': user.skills or '',
            'experience': user.experience_years or 0,
            'bio': user.bio or '',
        }
        advice = ai_service.get_career_advice(question, context)
        return jsonify({'success': True, 'advice': advice}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Career advice failed: {str(e)}'}), 500


# ============================================================
# IMPROVE RESUME
# ============================================================

@ai_bp.route('/improve-resume', methods=['POST'])
@jwt_required()
def improve_resume():
    """Get AI suggestions to improve a resume."""
    data = request.get_json(silent=True) or {}
    
    resume_text = data.get('resume_text', '').strip()
    target_role = data.get('target_role', '').strip()
    
    if not resume_text:
        return jsonify({'success': False, 'message': 'resume_text is required'}), 400
    
    try:
        suggestions = ai_service.improve_resume(resume_text, target_role)
        return jsonify({'success': True, 'suggestions': suggestions}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Resume improvement failed: {str(e)}'}), 500


# ============================================================
# INTERVIEW PREPARATION
# ============================================================

@ai_bp.route('/interview-prep', methods=['POST'])
@jwt_required()
def interview_prep():
    """Generate AI-powered interview questions for a specific job role."""
    data = request.get_json(silent=True) or {}
    
    job_title = data.get('job_title', '').strip()
    job_description = data.get('job_description', '').strip()
    
    if not job_title:
        return jsonify({'success': False, 'message': 'job_title is required'}), 400
    
    try:
        questions = ai_service.generate_interview_questions(job_title, job_description)
        return jsonify({'success': True, 'questions': questions}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Interview prep failed: {str(e)}'}), 500
