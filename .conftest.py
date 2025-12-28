"""
Pytest configuration and shared fixtures for EduPace tests
"""
import pytest
from django.contrib.auth.models import User
from edupace_app.models import (
    Student, Teacher, AcademicBoard, Course,
    ProgramOutcome, LearningOutcome, Grade,
    Assessment, AssessmentGrade, AssessmentToLO, LOToPO
)


@pytest.fixture
def user(db):
    """Create a basic user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def student_user(db):
    """Create a user with student profile"""
    user = User.objects.create_user(
        username='student1',
        email='student@example.com',
        password='testpass123',
        first_name='John',
        last_name='Student'
    )
    Student.objects.create(
        user=user,
        student_id='STU001',
        enrollment_date='2024-01-01',
        program='Computer Science'
    )
    return user


@pytest.fixture
def teacher_user(db):
    """Create a user with teacher profile"""
    user = User.objects.create_user(
        username='teacher1',
        email='teacher@example.com',
        password='testpass123',
        first_name='Jane',
        last_name='Teacher'
    )
    Teacher.objects.create(
        user=user,
        employee_id='TCH001',
        department='Computer Science'
    )
    return user


@pytest.fixture
def academic_board_user(db):
    """Create a user with academic board profile"""
    user = User.objects.create_user(
        username='board1',
        email='board@example.com',
        password='testpass123',
        first_name='Admin',
        last_name='Board'
    )
    AcademicBoard.objects.create(
        user=user,
        employee_id='AB001',
        designation='Dean'
    )
    return user


@pytest.fixture
def course(db, academic_board_user):
    """Create a test course"""
    return Course.objects.create(
        code='CS101',
        name='Introduction to Computer Science',
        description='Basic computer science concepts',
        credits=3,
        is_locked=False
    )


@pytest.fixture
def locked_course(db, academic_board_user):
    """Create a locked test course"""
    return Course.objects.create(
        code='CS102',
        name='Advanced Computer Science',
        description='Advanced topics',
        credits=3,
        is_locked=True
    )

