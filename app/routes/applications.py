"""
Application Routes
===================
Handle job applications: apply, track status, employer review.

WHY THIS FILE EXISTS:
    Applications are the transactional core — connecting job seekers
    to job listings. Separated from jobs.py because applications have
    their own lifecycle (apply → review → interview → offer).
    
Endpoints:
    POST   /api/applications                - Apply to a job
    GET    /api/applications                 - List my applications
    GET    /api/applications/<id>            - Get application details
    PUT    /api/applications/<id>/status     - Update status (employer)
    DELETE /api/applications/<id>            - Withdraw application
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.application import Application
from app.models.job import Job
from app.models.user import User

applications_bp = Blueprint('applications', __name__)


@applications_bp.route('', methods=['POST'])
@jwt_required()
def apply_to_job():
    """Submit a job application."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    job_id = data.get('job_id')
    if not job_id:
        return jsonify({'success': False, 'message': 'job_id is required'}), 400
    
    job = db.session.get(Job, job_id)
    if not job or job.status != 'active':
        return jsonify({'success': False, 'message': 'Job not found or no longer active'}), 404
    
    # Check for duplicate application
    existing = Application.query.filter_by(user_id=int(user_id), job_id=job_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'You have already applied to this job'}), 409
    
    application = Application(
        user_id=int(user_id),
        job_id=job_id,
        resume_id=data.get('resume_id'),
        cover_letter=data.get('cover_letter'),
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Application submitted successfully',
        'application': application.to_dict(),
    }), 201


@applications_bp.route('', methods=['GET'])
@jwt_required()
def list_applications():
    """List all applications for the current user."""
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    
    if user.role == 'employer':
        # Employers see applications for their posted jobs
        jobs = Job.query.filter_by(employer_id=user.id).all()
        job_ids = [j.id for j in jobs]
        apps = Application.query.filter(Application.job_id.in_(job_ids)).all()
    else:
        # Job seekers see their own applications
        apps = Application.query.filter_by(user_id=int(user_id)).all()
    
    return jsonify({
        'success': True,
        'applications': [app.to_dict() for app in apps],
        'total': len(apps),
    }), 200


@applications_bp.route('/<int:app_id>', methods=['GET'])
@jwt_required()
def get_application(app_id):
    """Get a single application's details."""
    user_id = get_jwt_identity()
    application = db.session.get(Application, app_id)
    
    if not application:
        return jsonify({'success': False, 'message': 'Application not found'}), 404
    
    # Only the applicant or the job's employer can view
    job = db.session.get(Job, application.job_id)
    if application.user_id != int(user_id) and job.employer_id != int(user_id):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    return jsonify({'success': True, 'application': application.to_dict()}), 200


@applications_bp.route('/<int:app_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status(app_id):
    """Update application status (employer only)."""
    user_id = get_jwt_identity()
    application = db.session.get(Application, app_id)
    
    if not application:
        return jsonify({'success': False, 'message': 'Application not found'}), 404
    
    job = db.session.get(Job, application.job_id)
    if job.employer_id != int(user_id):
        return jsonify({'success': False, 'message': 'Only the employer can update status'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    valid_statuses = ['applied', 'reviewed', 'shortlisted', 'interview', 'offered', 'hired', 'rejected']
    
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': f'Invalid status. Must be one of: {valid_statuses}'}), 400
    
    application.status = new_status
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Application status updated to {new_status}',
        'application': application.to_dict(),
    }), 200


@applications_bp.route('/<int:app_id>', methods=['DELETE'])
@jwt_required()
def withdraw_application(app_id):
    """Withdraw a job application (applicant only)."""
    user_id = get_jwt_identity()
    application = db.session.get(Application, app_id)
    
    if not application:
        return jsonify({'success': False, 'message': 'Application not found'}), 404
    
    if application.user_id != int(user_id):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    db.session.delete(application)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Application withdrawn'}), 200
