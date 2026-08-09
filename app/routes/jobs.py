"""
Job Listing Routes
===================
Full CRUD operations for job listings with search and filtering.

WHY THIS FILE EXISTS:
    Jobs are the main content of the platform. This blueprint handles
    creating, reading, updating, deleting, and searching job listings.
    
Endpoints:
    GET    /api/jobs              - List all jobs (with filters)
    GET    /api/jobs/<id>         - Get single job details
    POST   /api/jobs              - Create new job (employer only)
    PUT    /api/jobs/<id>         - Update job (owner only)
    DELETE /api/jobs/<id>         - Delete job (owner only)
    GET    /api/jobs/search       - Search jobs by keyword/skill
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.job import Job
from app.models.user import User

jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.route('', methods=['GET'])
def list_jobs():
    """List all active jobs with optional filtering."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    job_type = request.args.get('job_type')
    location = request.args.get('location')
    
    query = Job.query.filter_by(status='active')
    
    if job_type:
        query = query.filter_by(job_type=job_type)
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    
    query = query.order_by(Job.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'success': True,
        'jobs': [job.to_dict() for job in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
    }), 200


@jobs_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get a single job listing by ID."""
    job = db.session.get(Job, job_id)
    
    if not job:
        return jsonify({'success': False, 'message': 'Job not found'}), 404
    
    return jsonify({'success': True, 'job': job.to_dict()}), 200


@jobs_bp.route('', methods=['POST'])
@jwt_required()
def create_job():
    """Create a new job listing (employers only)."""
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    
    if not user or user.role not in ('employer', 'admin'):
        return jsonify({'success': False, 'message': 'Only employers can post jobs'}), 403
    
    data = request.get_json()
    
    required_fields = ['title', 'company', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'{field} is required'}), 400
    
    job = Job(
        title=data['title'],
        company=data['company'],
        description=data['description'],
        location=data.get('location'),
        job_type=data.get('job_type', 'full-time'),
        salary_min=data.get('salary_min'),
        salary_max=data.get('salary_max'),
        currency=data.get('currency', 'INR'),
        required_skills=','.join(data['required_skills']) if isinstance(data.get('required_skills'), list) else data.get('required_skills'),
        experience_required=data.get('experience_required', 0),
        education_level=data.get('education_level'),
        employer_id=user.id,
    )
    
    db.session.add(job)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Job created successfully',
        'job': job.to_dict(),
    }), 201


@jobs_bp.route('/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    """Update an existing job listing (owner only)."""
    user_id = get_jwt_identity()
    job = db.session.get(Job, job_id)
    
    if not job:
        return jsonify({'success': False, 'message': 'Job not found'}), 404
    
    if job.employer_id != int(user_id):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    updatable = ['title', 'company', 'description', 'location', 'job_type',
                 'salary_min', 'salary_max', 'status', 'required_skills',
                 'experience_required', 'education_level']
    
    for field in updatable:
        if field in data:
            if field == 'required_skills' and isinstance(data[field], list):
                setattr(job, field, ','.join(data[field]))
            else:
                setattr(job, field, data[field])
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Job updated', 'job': job.to_dict()}), 200


@jobs_bp.route('/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    """Delete a job listing (owner only)."""
    user_id = get_jwt_identity()
    job = db.session.get(Job, job_id)
    
    if not job:
        return jsonify({'success': False, 'message': 'Job not found'}), 404
    
    if job.employer_id != int(user_id):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    db.session.delete(job)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Job deleted'}), 200


@jobs_bp.route('/search', methods=['GET'])
def search_jobs():
    """Search jobs by keyword across title, description, and skills."""
    keyword = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if not keyword:
        return jsonify({'success': False, 'message': 'Search query (q) is required'}), 400
    
    query = Job.query.filter(
        Job.status == 'active',
        db.or_(
            Job.title.ilike(f'%{keyword}%'),
            Job.description.ilike(f'%{keyword}%'),
            Job.required_skills.ilike(f'%{keyword}%'),
            Job.company.ilike(f'%{keyword}%'),
        )
    ).order_by(Job.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'success': True,
        'jobs': [job.to_dict() for job in pagination.items],
        'total': pagination.total,
        'query': keyword,
    }), 200
