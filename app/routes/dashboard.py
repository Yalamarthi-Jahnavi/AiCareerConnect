"""
Dashboard Routes
==================
Dynamic dashboard data endpoints for real-time analytics.

WHY THIS FILE EXISTS:
    The dashboard needs aggregated, computed data that doesn't map to
    simple CRUD operations. These endpoints provide statistics, charts,
    and activity feeds customized per user role (job seeker vs employer).
    
Endpoints:
    GET /api/dashboard/stats           - Overall platform statistics
    GET /api/dashboard/job-seeker      - Job seeker personal dashboard
    GET /api/dashboard/employer        - Employer hiring dashboard
    GET /api/dashboard/activity        - Recent activity feed
    GET /api/dashboard/skill-trends    - Trending skills analytics
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app.extensions import db
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.models.resume import Resume

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def platform_stats():
    """Get overall platform statistics."""
    stats = {
        'total_users': User.query.count(),
        'total_jobs': Job.query.filter_by(status='active').count(),
        'total_applications': Application.query.count(),
        'total_resumes': Resume.query.count(),
        'jobs_by_type': _get_jobs_by_type(),
        'applications_by_status': _get_applications_by_status(),
        'recent_jobs': [job.to_dict() for job in Job.query.order_by(Job.created_at.desc()).limit(5).all()],
    }
    
    return jsonify({'success': True, 'stats': stats}), 200


@dashboard_bp.route('/job-seeker', methods=['GET'])
@jwt_required()
def job_seeker_dashboard():
    """Get personalized dashboard data for a job seeker."""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # My applications breakdown
    my_apps = Application.query.filter_by(user_id=user.id).all()
    status_counts = {}
    for app in my_apps:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1
    
    # My resumes
    my_resumes = Resume.query.filter_by(user_id=user.id).all()
    
    # Recommended jobs count (jobs matching user skills)
    matching_jobs_count = 0
    if user.skills:
        user_skill_list = [s.strip().lower() for s in user.skills.split(',')]
        for skill in user_skill_list:
            matching_jobs_count += Job.query.filter(
                Job.status == 'active',
                Job.required_skills.ilike(f'%{skill}%')
            ).count()
    
    dashboard_data = {
        'profile_completeness': _calculate_profile_completeness(user),
        'total_applications': len(my_apps),
        'application_status_breakdown': status_counts,
        'resumes_uploaded': len(my_resumes),
        'matching_jobs_available': matching_jobs_count,
        'recent_applications': [app.to_dict() for app in my_apps[-5:]],
        'interview_count': status_counts.get('interview', 0),
        'offers_count': status_counts.get('offered', 0),
    }
    
    return jsonify({'success': True, 'dashboard': dashboard_data}), 200


@dashboard_bp.route('/employer', methods=['GET'])
@jwt_required()
def employer_dashboard():
    """Get hiring dashboard data for an employer."""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user or user.role not in ('employer', 'admin'):
        return jsonify({'success': False, 'message': 'Employer access required'}), 403
    
    # My posted jobs
    my_jobs = Job.query.filter_by(employer_id=user.id).all()
    
    # Applications per job
    jobs_with_stats = []
    total_applicants = 0
    for job in my_jobs:
        app_count = Application.query.filter_by(job_id=job.id).count()
        total_applicants += app_count
        jobs_with_stats.append({
            **job.to_dict(),
            'application_count': app_count,
        })
    
    # Application status breakdown across all my jobs
    job_ids = [j.id for j in my_jobs]
    all_apps = Application.query.filter(Application.job_id.in_(job_ids)).all() if job_ids else []
    status_counts = {}
    for app in all_apps:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1
    
    dashboard_data = {
        'total_jobs_posted': len(my_jobs),
        'active_jobs': len([j for j in my_jobs if j.status == 'active']),
        'total_applicants': total_applicants,
        'application_status_breakdown': status_counts,
        'jobs': jobs_with_stats,
        'hired_count': status_counts.get('hired', 0),
    }
    
    return jsonify({'success': True, 'dashboard': dashboard_data}), 200


@dashboard_bp.route('/activity', methods=['GET'])
@jwt_required()
def recent_activity():
    """Get recent activity feed for the current user."""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    activities = []
    
    # Recent applications
    recent_apps = Application.query.filter_by(user_id=user.id)\
        .order_by(Application.applied_at.desc()).limit(10).all()
    
    for app in recent_apps:
        job = Job.query.get(app.job_id)
        activities.append({
            'type': 'application',
            'message': f'Applied to {job.title} at {job.company}' if job else 'Applied to a job',
            'status': app.status,
            'timestamp': app.applied_at.isoformat() if app.applied_at else None,
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return jsonify({'success': True, 'activities': activities[:20]}), 200


@dashboard_bp.route('/skill-trends', methods=['GET'])
def skill_trends():
    """Get trending skills based on active job listings."""
    active_jobs = Job.query.filter_by(status='active').all()
    
    skill_count = {}
    for job in active_jobs:
        if job.required_skills:
            skills = [s.strip().lower() for s in job.required_skills.split(',')]
            for skill in skills:
                if skill:
                    skill_count[skill] = skill_count.get(skill, 0) + 1
    
    # Sort by frequency and return top 20
    trending = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:20]
    
    return jsonify({
        'success': True,
        'trending_skills': [{'skill': s, 'demand_count': c} for s, c in trending],
    }), 200


# ─── Helper Functions ───────────────────────────────────────────────

def _calculate_profile_completeness(user):
    """Calculate how complete a user's profile is (0-100%)."""
    fields = ['full_name', 'phone', 'location', 'bio', 'skills', 'experience_years']
    filled = sum(1 for f in fields if getattr(user, f, None))
    return round((filled / len(fields)) * 100)


def _get_jobs_by_type():
    """Get job count grouped by job type."""
    results = db.session.query(Job.job_type, func.count(Job.id))\
        .filter_by(status='active').group_by(Job.job_type).all()
    return {job_type: count for job_type, count in results}


def _get_applications_by_status():
    """Get application count grouped by status."""
    results = db.session.query(Application.status, func.count(Application.id))\
        .group_by(Application.status).all()
    return {status: count for status, count in results}
