"""
Job Service
=============
Business logic for job listing operations.

WHY THIS FILE EXISTS:
    Complex job search, filtering, and recommendation logic lives here.
    Routes stay thin — they only handle HTTP request/response.
    The service is independently testable without Flask context.
"""

from app.extensions import db
from app.models.job import Job


class JobService:
    """Handles job listing business logic."""
    
    @staticmethod
    def search_jobs(keyword='', location='', job_type='', min_salary=None,
                    skills=None, page=1, per_page=10):
        """
        Advanced job search with multiple filters.
        
        Args:
            keyword: Search term for title/description
            location: Filter by location
            job_type: Filter by job type
            min_salary: Minimum salary filter
            skills: List of required skills
            page: Page number
            per_page: Results per page
            
        Returns:
            dict: Paginated search results
        """
        query = Job.query.filter_by(status='active')
        
        if keyword:
            query = query.filter(
                db.or_(
                    Job.title.ilike(f'%{keyword}%'),
                    Job.description.ilike(f'%{keyword}%'),
                    Job.company.ilike(f'%{keyword}%'),
                )
            )
        
        if location:
            query = query.filter(Job.location.ilike(f'%{location}%'))
        
        if job_type:
            query = query.filter_by(job_type=job_type)
        
        if min_salary is not None:
            query = query.filter(Job.salary_min >= min_salary)
        
        if skills:
            for skill in skills:
                query = query.filter(Job.required_skills.ilike(f'%{skill}%'))
        
        query = query.order_by(Job.is_featured.desc(), Job.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'jobs': [job.to_dict() for job in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
        }
    
    @staticmethod
    def get_similar_jobs(job_id, limit=5):
        """Find jobs similar to a given job based on skills and title."""
        job = Job.query.get(job_id)
        if not job:
            return []
        
        # Find jobs with overlapping skills
        similar = Job.query.filter(
            Job.id != job_id,
            Job.status == 'active',
            db.or_(
                Job.required_skills.ilike(f'%{skill.strip()}%')
                for skill in (job.required_skills or '').split(',')
                if skill.strip()
            ) if job.required_skills else db.true()
        ).limit(limit).all()
        
        return [j.to_dict() for j in similar]
