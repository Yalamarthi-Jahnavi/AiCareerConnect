"""
Job Tests
===========
Tests for job listing CRUD and search operations.

WHY THIS FILE EXISTS:
    Verifies job creation (employers only), listing, searching, and
    role-based access control on job endpoints.
"""

from app.models.job import Job


class TestJobListing:
    """Tests for the /api/jobs endpoints."""
    
    def test_list_jobs_empty(self, client, db_session):
        """Test listing jobs when none exist."""
        response = client.get('/api/jobs')
        assert response.status_code == 200
        data = response.get_json()
        assert data['jobs'] == []
    
    def test_create_job_as_employer(self, client, sample_employer, db_session):
        """Test that employers can create jobs."""
        # Login as employer
        login_resp = client.post('/api/auth/login', json={
            'email': 'employer@example.com',
            'password': 'TestPass123',
        })
        token = login_resp.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.post('/api/jobs', json={
            'title': 'Python Developer',
            'company': 'Tech Corp',
            'description': 'Build amazing things with Python',
            'location': 'Hyderabad',
            'required_skills': ['Python', 'Flask', 'SQL'],
        }, headers=headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['job']['title'] == 'Python Developer'
    
    def test_create_job_as_seeker_fails(self, client, auth_headers, db_session):
        """Test that job seekers cannot create jobs."""
        response = client.post('/api/jobs', json={
            'title': 'Should Fail',
            'company': 'Nope',
            'description': 'This should not work',
        }, headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_search_jobs(self, client, sample_employer, db_session):
        """Test job search functionality."""
        # Create a job first
        login_resp = client.post('/api/auth/login', json={
            'email': 'employer@example.com',
            'password': 'TestPass123',
        })
        token = login_resp.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        client.post('/api/jobs', json={
            'title': 'Flask Developer',
            'company': 'AI Corp',
            'description': 'Work with Flask and AI',
            'required_skills': 'Python,Flask,AI',
        }, headers=headers)
        
        # Search
        response = client.get('/api/jobs/search?q=Flask')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] >= 1
