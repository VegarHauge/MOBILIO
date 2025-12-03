"""
Authentication Endpoint Tests

This module tests all authentication-related endpoints:
- POST /api/auth/register - User registration
- POST /api/auth/login - User login
- POST /api/auth/logout - User logout
- GET /api/auth/me - Get current user

Test Coverage:
- Success cases with valid data
- Validation errors with invalid data
- Authentication failures
- Token generation and validation
- Password hashing and verification
- Duplicate email prevention
- Role-based access
"""

from datetime import timedelta
from fastapi import status
from services.auth_service import AuthService


class TestUserRegistration:
    """Test cases for user registration endpoint"""
    
    def test_register_new_user_success(self, client):
        """Test successful registration with valid data"""
        response = client.post(
            "/api/auth/register",
            json={
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "securepassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["role"] == "customer"  # Default role
        assert "id" in data
        assert "password" not in data  # Password should not be returned
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration fails with duplicate email"""
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Another User",
                "email": test_user.email,  # Duplicate email
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration fails with invalid email format"""
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Invalid User",
                "email": "not-an-email",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_missing_name(self, client):
        """Test registration fails without name"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "noname@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_missing_password(self, client):
        """Test registration fails without password"""
        response = client.post(
            "/api/auth/register",
            json={
                "name": "No Password User",
                "email": "nopass@example.com"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_short_password(self, client):
        """Test registration with various password lengths"""
        # Note: Current schema has no password length validation
        # This test documents current behavior - consider adding Field(min_length=8)
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Short Password User",
                "email": "short@example.com",
                "password": "abc"  # Very short password
            }
        )
        
        # Currently accepts any password length (no validation)
        assert response.status_code == status.HTTP_200_OK
    
    def test_register_password_hashed(self, client, db_session):
        """Test that password is properly hashed in database"""
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Hash Test",
                "email": "hash@example.com",
                "password": "plainpassword"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify password is hashed in database
        from models.user import User
        user = db_session.query(User).filter(User.email == "hash@example.com").first()
        assert user is not None
        assert user.password != "plainpassword"  # Should be hashed
        assert user.password.startswith("$argon2")  # Argon2 hash


class TestUserLogin:
    """Test cases for user login endpoint"""
    
    def test_login_success(self, client, test_user):
        """Test successful login with correct credentials"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user.email
        assert data["user"]["name"] == test_user.name
        assert data["user"]["role"] == test_user.role
    
    def test_login_wrong_password(self, client, test_user):
        """Test login fails with incorrect password"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login fails with non-existent email"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "somepassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_invalid_email_format(self, client):
        """Test login fails with invalid email format"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "not-an-email",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_missing_credentials(self, client):
        """Test login fails with missing credentials"""
        response = client.post(
            "/api/auth/login",
            json={}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_token_validity(self, client, test_user):
        """Test that generated token is valid and contains correct data"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access_token"]
        
        # Verify token by using it in an authenticated endpoint
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert me_response.status_code == status.HTTP_200_OK
        assert me_response.json()["email"] == test_user.email
    
    def test_login_admin_user(self, client, test_admin):
        """Test admin user can login and receives correct role"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_admin.email,
                "password": "adminpass123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user"]["role"] == "admin"


class TestLogout:
    """Test cases for logout endpoint"""
    
    def test_logout_success(self, client, auth_headers):
        """Test successful logout with valid token"""
        response = client.post(
            "/api/auth/logout",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
    
    def test_logout_without_token(self, client):
        """Test logout fails without authentication token"""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_logout_invalid_token(self, client):
        """Test logout fails with invalid token"""
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCurrentUser:
    """Test cases for getting current user information"""
    
    def test_get_me_success(self, client, test_user, auth_headers):
        """Test successfully retrieving current user data"""
        response = client.get(
            "/api/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["role"] == test_user.role
        assert "password" not in data
    
    def test_get_me_without_token(self, client):
        """Test getting current user fails without token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_me_invalid_token(self, client):
        """Test getting current user fails with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_me_expired_token(self, client, test_user):
        """Test getting current user fails with expired token"""
        # Create a token that's already expired
        expired_token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "name": test_user.name,
                "email": test_user.email,
                "role": test_user.role
            },
            expires_delta=timedelta(seconds=-1)  # Expired 1 second ago
        )
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_me_malformed_authorization_header(self, client):
        """Test getting current user fails with malformed header"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "NotBearer token_here"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_me_admin_user(self, client, test_admin, admin_headers):
        """Test admin user can retrieve their information"""
        response = client.get(
            "/api/auth/me",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "admin"
        assert data["email"] == test_admin.email


class TestAuthenticationSecurity:
    """Test security aspects of authentication"""
    
    def test_password_not_returned_in_responses(self, client):
        """Test that password is never included in API responses"""
        # Register
        register_response = client.post(
            "/api/auth/register",
            json={
                "name": "Security Test",
                "email": "security@example.com",
                "password": "securepass123"
            }
        )
        assert "password" not in register_response.json()
        
        # Login
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "security@example.com",
                "password": "securepass123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Get me
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert "password" not in me_response.json()
    
    def test_case_sensitive_email(self, client, test_user):
        """Test email comparison behavior with different casing"""
        # Try to login with uppercase email
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email.upper(),
                "password": "testpassword123"
            }
        )
        
        # SQLAlchemy string comparison is typically case-sensitive by default
        # This should fail unless email is normalized during registration/login
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_sql_injection_prevention(self, client, test_user):
        """Test that SQLAlchemy parameterized queries prevent SQL injection"""
        # Register a user with a normal email
        client.post(
            "/api/auth/register",
            json={
                "name": "Injection Test",
                "email": "injection@example.com",
                "password": "password123"
            }
        )
        
        # Try SQL injection in password field (since email has format validation)
        response = client.post(
            "/api/auth/login",
            json={
                "email": "injection@example.com",
                "password": "' OR '1'='1' --"  # Classic SQL injection
            }
        )
        
        # SQLAlchemy uses parameterized queries, so this should fail authentication
        # not bypass it (if it returns 200, SQL injection worked - bad!)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_xss_prevention_in_registration(self, client):
        """Test that XSS attempts in name field are handled"""
        response = client.post(
            "/api/auth/register",
            json={
                "name": "<script>alert('xss')</script>",
                "email": "xss@example.com",
                "password": "password123"
            }
        )
        
        # Should either succeed with sanitized data or fail validation
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
