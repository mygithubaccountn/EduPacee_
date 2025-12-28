"""
Integration tests for authentication and authorization views
"""
import pytest
from django.urls import reverse
from django.contrib.auth.models import User

from edupace_app.factories import (
    StudentFactory, TeacherFactory, AcademicBoardFactory, CourseFactory
)


class TestLoginView:
    """Tests for login view"""
    
    def test_login_page_loads(self, client):
        """Test that login page loads"""
        response = client.get(reverse('edupace_app:login'))
        assert response.status_code == 200
        assert 'form' in response.context
    
    def test_login_redirects_authenticated_user(self, client, student_user):
        """Test that authenticated users are redirected"""
        client.force_login(student_user)
        response = client.get(reverse('edupace_app:login'))
        assert response.status_code == 302  # Redirect
    
    def test_login_with_valid_credentials(self, client):
        """Test login with valid credentials"""
        student = StudentFactory()
        response = client.post(reverse('edupace_app:login'), {
            'username': student.user.username,
            'password': 'testpass123',
            'role': 'student'
        })
        assert response.status_code == 302  # Redirect after login
    
    def test_login_with_wrong_role(self, client):
        """Test login with wrong role selection"""
        student = StudentFactory()
        response = client.post(reverse('edupace_app:login'), {
            'username': student.user.username,
            'password': 'testpass123',
            'role': 'teacher'  # Wrong role
        })
        assert response.status_code == 200  # Stays on login page
        assert 'not registered' in response.content.decode().lower()
    
    def test_login_with_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post(reverse('edupace_app:login'), {
            'username': 'nonexistent',
            'password': 'wrongpass',
            'role': 'student'
        })
        assert response.status_code == 200  # Stays on login page


class TestLogoutView:
    """Tests for logout view"""
    
    def test_logout_requires_login(self, client):
        """Test that logout requires authentication"""
        response = client.get(reverse('edupace_app:logout'))
        assert response.status_code == 302  # Redirect to login
    
    def test_logout_logs_out_user(self, client, student_user):
        """Test that logout logs out the user"""
        client.force_login(student_user)
        response = client.post(reverse('edupace_app:logout'))
        assert response.status_code == 302  # Redirect
        # User should be logged out
        response = client.get(reverse('edupace_app:student_dashboard'))
        assert response.status_code == 302  # Should redirect to login


class TestDashboardRedirect:
    """Tests for dashboard redirect view"""
    
    def test_redirect_requires_login(self, client):
        """Test that dashboard redirect requires authentication"""
        response = client.get(reverse('edupace_app:dashboard_redirect'))
        assert response.status_code == 302  # Redirect to login
    
    def test_redirect_student_to_student_dashboard(self, client, student_user):
        """Test that students are redirected to student dashboard"""
        client.force_login(student_user)
        response = client.get(reverse('edupace_app:dashboard_redirect'))
        assert response.status_code == 302
        assert 'student' in response.url.lower()
    
    def test_redirect_teacher_to_teacher_dashboard(self, client, teacher_user):
        """Test that teachers are redirected to teacher dashboard"""
        client.force_login(teacher_user)
        response = client.get(reverse('edupace_app:dashboard_redirect'))
        assert response.status_code == 302
        assert 'teacher' in response.url.lower()
    
    def test_redirect_academic_board_to_board_dashboard(self, client, academic_board_user):
        """Test that academic board are redirected to board dashboard"""
        client.force_login(academic_board_user)
        response = client.get(reverse('edupace_app:dashboard_redirect'))
        assert response.status_code == 302
        assert 'academic_board' in response.url.lower() or 'board' in response.url.lower()


class TestRoleBasedAccess:
    """Tests for role-based access control"""
    
    def test_student_cannot_access_teacher_dashboard(self, client, student_user):
        """Test that students cannot access teacher dashboard"""
        client.force_login(student_user)
        response = client.get(reverse('edupace_app:teacher_dashboard'))
        assert response.status_code == 302  # Redirect (permission denied)
    
    def test_teacher_cannot_access_student_dashboard(self, client, teacher_user):
        """Test that teachers cannot access student dashboard"""
        client.force_login(teacher_user)
        response = client.get(reverse('edupace_app:student_dashboard'))
        assert response.status_code == 302  # Redirect (permission denied)
    
    def test_student_cannot_access_academic_board_dashboard(self, client, student_user):
        """Test that students cannot access academic board dashboard"""
        client.force_login(student_user)
        response = client.get(reverse('edupace_app:academic_board_dashboard'))
        assert response.status_code == 302  # Redirect (permission denied)
    
    def test_teacher_can_access_teacher_dashboard(self, client, teacher_user):
        """Test that teachers can access their dashboard"""
        client.force_login(teacher_user)
        response = client.get(reverse('edupace_app:teacher_dashboard'))
        assert response.status_code == 200
    
    def test_student_can_access_student_dashboard(self, client, student_user):
        """Test that students can access their dashboard"""
        client.force_login(student_user)
        response = client.get(reverse('edupace_app:student_dashboard'))
        assert response.status_code == 200
    
    def test_academic_board_can_access_board_dashboard(self, client, academic_board_user):
        """Test that academic board can access their dashboard"""
        client.force_login(academic_board_user)
        response = client.get(reverse('edupace_app:academic_board_dashboard'))
        assert response.status_code == 200

