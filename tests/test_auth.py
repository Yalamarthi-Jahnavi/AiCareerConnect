"""
Auth Tests
============
Tests for registration, login, and token management.

WHY THIS FILE EXISTS:
    Verifies that authentication works correctly — registration creates
    users, login returns valid tokens, and protected routes reject
    unauthenticated requests.
"""


class TestRegistration:
    """Tests for the /api/auth/register endpoint."""
    
    def test_register_success(self, client, db_session):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePass123',
            'full_name': 'New User',
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'access_token' in data
        assert data['user']['username'] == 'newuser'
    
    def test_register_duplicate_email(self, client, sample_user):
        """Test that duplicate emails are rejected."""
        response = client.post('/api/auth/register', json={
            'username': 'different',
            'email': 'test@example.com',  # Already exists
            'password': 'SecurePass123',
        })
        
        assert response.status_code == 409
    
    def test_register_missing_fields(self, client, db_session):
        """Test that missing fields return 400."""
        response = client.post('/api/auth/register', json={
            'username': 'incomplete',
        })
        
        assert response.status_code == 400


class TestLogin:
    """Tests for the /api/auth/login endpoint."""
    
    def test_login_success(self, client, sample_user):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass123',
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'access_token' in data
        assert 'refresh_token' in data
    
    def test_login_wrong_password(self, client, sample_user):
        """Test login with incorrect password."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword',
        })
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client, db_session):
        """Test login with non-existent email."""
        response = client.post('/api/auth/login', json={
            'email': 'nobody@example.com',
            'password': 'password',
        })
        
        assert response.status_code == 401


class TestProtectedRoutes:
    """Tests for JWT-protected route access."""
    
    def test_access_protected_route_with_token(self, client, auth_headers):
        """Test that authenticated requests succeed."""
        response = client.get('/api/auth/me', headers=auth_headers)
        assert response.status_code == 200
    
    def test_access_protected_route_without_token(self, client):
        """Test that unauthenticated requests are rejected."""
        response = client.get('/api/auth/me')
        assert response.status_code == 401
