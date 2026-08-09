"""
Application Tests
===================
Tests for job application submission and tracking.

WHY THIS FILE EXISTS:
    Verifies the application lifecycle: apply, view, update status,
    withdraw. Also checks that duplicate applications are prevented.
"""


class TestApplications:
    """Tests for the /api/applications endpoints."""
    
    def test_apply_to_job(self, client, sample_user, sample_employer, db_session):
        """Test applying to a job."""
        # Create a job as employer
        login_resp = client.post('/api/auth/login', json={
            'email': 'employer@example.com',
            'password': 'TestPass123',
        })
        emp_token = login_resp.get_json()['access_token']
        emp_headers = {'Authorization': f'Bearer {emp_token}'}
        
        job_resp = client.post('/api/jobs', json={
            'title': 'Test Job',
            'company': 'Test Corp',
            'description': 'A test job listing',
        }, headers=emp_headers)
        job_id = job_resp.get_json()['job']['id']
        
        # Apply as job seeker
        login_resp = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass123',
        })
        seeker_token = login_resp.get_json()['access_token']
        seeker_headers = {'Authorization': f'Bearer {seeker_token}'}
        
        response = client.post('/api/applications', json={
            'job_id': job_id,
            'cover_letter': 'I am very interested in this role.',
        }, headers=seeker_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['application']['status'] == 'applied'
    
    def test_duplicate_application_rejected(self, client, sample_user, sample_employer, db_session):
        """Test that applying twice to the same job is rejected."""
        # Setup: Create job and apply once
        login_resp = client.post('/api/auth/login', json={
            'email': 'employer@example.com',
            'password': 'TestPass123',
        })
        emp_token = login_resp.get_json()['access_token']
        
        job_resp = client.post('/api/jobs', json={
            'title': 'Unique Job',
            'company': 'Corp',
            'description': 'Only one application allowed',
        }, headers={'Authorization': f'Bearer {emp_token}'})
        job_id = job_resp.get_json()['job']['id']
        
        login_resp = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass123',
        })
        seeker_token = login_resp.get_json()['access_token']
        seeker_headers = {'Authorization': f'Bearer {seeker_token}'}
        
        # First application - should succeed
        client.post('/api/applications', json={'job_id': job_id}, headers=seeker_headers)
        
        # Second application - should fail
        response = client.post('/api/applications', json={'job_id': job_id}, headers=seeker_headers)
        assert response.status_code == 409
