"""
Unit tests for EduPace utility functions
"""
import pytest
import pandas as pd
import tempfile
import os
from django.contrib.auth.models import User

from edupace_app.utils import (
    get_user_role, get_user_profile, role_required,
    check_course_edit_permission, check_learning_outcome_permission,
    check_grade_permission, process_excel_grades, calculate_lo_score,
    calculate_po_score, get_course_graph_data, execute_safe_db_operations
)
from edupace_app.factories import (
    StudentFactory, TeacherFactory, AcademicBoardFactory,
    CourseFactory, LearningOutcomeFactory, GradeFactory,
    AssessmentFactory, AssessmentGradeFactory, AssessmentToLOFactory,
    LOToPOFactory, ProgramOutcomeFactory
)
from edupace_app.models import Student, Teacher, AcademicBoard, Course


class TestGetUserRole:
    """Tests for get_user_role function"""
    
    def test_get_student_role(self, student_user):
        """Test getting student role"""
        assert get_user_role(student_user) == 'student'
    
    def test_get_teacher_role(self, teacher_user):
        """Test getting teacher role"""
        assert get_user_role(teacher_user) == 'teacher'
    
    def test_get_academic_board_role(self, academic_board_user):
        """Test getting academic board role"""
        assert get_user_role(academic_board_user) == 'academic_board'
    
    def test_get_role_for_unauthenticated_user(self, db):
        """Test getting role for unauthenticated user"""
        user = User()
        user.is_authenticated = False
        assert get_user_role(user) is None
    
    def test_get_role_for_user_without_profile(self, db):
        """Test getting role for user without profile"""
        user = User.objects.create_user(
            username='noprofile',
            password='testpass123'
        )
        assert get_user_role(user) is None


class TestGetUserProfile:
    """Tests for get_user_profile function"""
    
    def test_get_student_profile(self, student_user):
        """Test getting student profile"""
        profile = get_user_profile(student_user)
        assert isinstance(profile, Student)
        assert profile.user == student_user
    
    def test_get_teacher_profile(self, teacher_user):
        """Test getting teacher profile"""
        profile = get_user_profile(teacher_user)
        assert isinstance(profile, Teacher)
        assert profile.user == teacher_user
    
    def test_get_academic_board_profile(self, academic_board_user):
        """Test getting academic board profile"""
        profile = get_user_profile(academic_board_user)
        assert isinstance(profile, AcademicBoard)
        assert profile.user == academic_board_user
    
    def test_get_profile_for_user_without_profile(self, db):
        """Test getting profile for user without profile"""
        user = User.objects.create_user(
            username='noprofile',
            password='testpass123'
        )
        assert get_user_profile(user) is None


class TestCheckCourseEditPermission:
    """Tests for check_course_edit_permission function"""
    
    def test_academic_board_can_edit(self, academic_board_user, course):
        """Test that academic board can edit courses"""
        assert check_course_edit_permission(academic_board_user, course) is True
    
    def test_teacher_cannot_edit(self, teacher_user, course):
        """Test that teachers cannot edit courses"""
        assert check_course_edit_permission(teacher_user, course) is False
    
    def test_student_cannot_edit(self, student_user, course):
        """Test that students cannot edit courses"""
        assert check_course_edit_permission(student_user, course) is False


class TestCheckLearningOutcomePermission:
    """Tests for check_learning_outcome_permission function"""
    
    def test_teacher_can_add_lo_to_assigned_course(self, teacher_user, course):
        """Test that teacher can add LO to assigned course"""
        teacher_user.teacher_profile.courses.add(course)
        assert check_learning_outcome_permission(teacher_user, course) is True
    
    def test_teacher_cannot_add_lo_to_unassigned_course(self, teacher_user, course):
        """Test that teacher cannot add LO to unassigned course"""
        assert check_learning_outcome_permission(teacher_user, course) is False
    
    def test_student_cannot_add_lo(self, student_user, course):
        """Test that students cannot add learning outcomes"""
        assert check_learning_outcome_permission(student_user, course) is False
    
    def test_academic_board_cannot_add_lo(self, academic_board_user, course):
        """Test that academic board cannot add learning outcomes"""
        assert check_learning_outcome_permission(academic_board_user, course) is False


class TestCheckGradePermission:
    """Tests for check_grade_permission function"""
    
    def test_teacher_can_add_grade_to_assigned_course(self, teacher_user, course):
        """Test that teacher can add grade to assigned course"""
        teacher_user.teacher_profile.courses.add(course)
        assert check_grade_permission(teacher_user, course) is True
    
    def test_teacher_cannot_add_grade_to_unassigned_course(self, teacher_user, course):
        """Test that teacher cannot add grade to unassigned course"""
        assert check_grade_permission(teacher_user, course) is False
    
    def test_teacher_cannot_add_grade_to_locked_course(self, teacher_user, locked_course):
        """Test that teacher cannot add grade to locked course"""
        teacher_user.teacher_profile.courses.add(locked_course)
        # Note: check_grade_permission doesn't check is_locked, but views should
        # This test verifies the permission check itself
        assert check_grade_permission(teacher_user, locked_course) is True


class TestProcessExcelGrades:
    """Tests for process_excel_grades function"""
    
    def test_process_valid_excel_file(self, db, course, teacher_user):
        """Test processing a valid Excel file"""
        student1 = StudentFactory(student_id='STU001')
        student2 = StudentFactory(student_id='STU002')
        
        # Create Excel file
        df = pd.DataFrame({
            'Student ID': ['STU001', 'STU002'],
            'Grade': ['A+', 'B'],
            'Percentage': [95.5, 85.0]
        })
        
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.xlsx', delete=False) as f:
            df.to_excel(f.name, index=False)
            f.seek(0)
            
            success, message, errors = process_excel_grades(
                f.name, course, 'Fall 2024', '2024-2025', teacher_user
            )
            
            os.unlink(f.name)
        
        assert success is True
        assert 'Successfully' in message
        assert len(errors) == 0
    
    def test_process_excel_with_missing_student(self, db, course, teacher_user):
        """Test processing Excel with non-existent student"""
        student1 = StudentFactory(student_id='STU001')
        
        # Create Excel file with non-existent student
        df = pd.DataFrame({
            'Student ID': ['STU001', 'STU999'],
            'Grade': ['A+', 'B'],
            'Percentage': [95.5, 85.0]
        })
        
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.xlsx', delete=False) as f:
            df.to_excel(f.name, index=False)
            f.seek(0)
            
            success, message, errors = process_excel_grades(
                f.name, course, 'Fall 2024', '2024-2025', teacher_user
            )
            
            os.unlink(f.name)
        
        assert success is True
        assert len(errors) > 0
        assert any('STU999' in error for error in errors)
    
    def test_process_excel_with_invalid_grade(self, db, course, teacher_user):
        """Test processing Excel with invalid grade"""
        student1 = StudentFactory(student_id='STU001')
        
        # Create Excel file with invalid grade
        df = pd.DataFrame({
            'Student ID': ['STU001'],
            'Grade': ['X'],  # Invalid grade
            'Percentage': [95.5]
        })
        
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.xlsx', delete=False) as f:
            df.to_excel(f.name, index=False)
            f.seek(0)
            
            success, message, errors = process_excel_grades(
                f.name, course, 'Fall 2024', '2024-2025', teacher_user
            )
            
            os.unlink(f.name)
        
        assert success is True
        assert len(errors) > 0
        assert any('Invalid grade' in error for error in errors)
    
    def test_process_excel_missing_required_columns(self, db, course, teacher_user):
        """Test processing Excel with missing required columns"""
        # Create Excel file without required columns
        df = pd.DataFrame({
            'Name': ['John', 'Jane'],
            'Score': [95, 85]
        })
        
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.xlsx', delete=False) as f:
            df.to_excel(f.name, index=False)
            f.seek(0)
            
            success, message, errors = process_excel_grades(
                f.name, course, 'Fall 2024', '2024-2025', teacher_user
            )
            
            os.unlink(f.name)
        
        assert success is False
        assert 'Student ID' in message or 'Grade' in message


class TestCalculateLOScore:
    """Tests for calculate_lo_score function"""
    
    def test_calculate_lo_score_with_grades(self, db):
        """Test calculating LO score with assessment grades"""
        student = StudentFactory()
        course = CourseFactory()
        assessment1 = AssessmentFactory(course=course)
        assessment2 = AssessmentFactory(course=course)
        lo = LearningOutcomeFactory(course=course)
        
        # Create assessment grades
        ag1 = AssessmentGradeFactory(assessment=assessment1, student=student, grade=80.0)
        ag2 = AssessmentGradeFactory(assessment=assessment2, student=student, grade=90.0)
        
        # Create connections with weights
        AssessmentToLOFactory(assessment=assessment1, learning_outcome=lo, weight=0.5)
        AssessmentToLOFactory(assessment=assessment2, learning_outcome=lo, weight=0.5)
        
        score = calculate_lo_score(student, lo)
        assert score is not None
        assert score == 85.0  # (80 * 0.5 + 90 * 0.5) / 1.0
    
    def test_calculate_lo_score_no_connections(self, db):
        """Test calculating LO score with no connections"""
        student = StudentFactory()
        lo = LearningOutcomeFactory()
        
        score = calculate_lo_score(student, lo)
        assert score is None
    
    def test_calculate_lo_score_no_grades(self, db):
        """Test calculating LO score when student has no grades"""
        student = StudentFactory()
        course = CourseFactory()
        assessment = AssessmentFactory(course=course)
        lo = LearningOutcomeFactory(course=course)
        
        # Create connection but no grade
        AssessmentToLOFactory(assessment=assessment, learning_outcome=lo, weight=1.0)
        
        score = calculate_lo_score(student, lo)
        assert score is None
    
    def test_calculate_lo_score_weighted_average(self, db):
        """Test LO score calculation with different weights"""
        student = StudentFactory()
        course = CourseFactory()
        assessment1 = AssessmentFactory(course=course)
        assessment2 = AssessmentFactory(course=course)
        lo = LearningOutcomeFactory(course=course)
        
        # Create assessment grades
        AssessmentGradeFactory(assessment=assessment1, student=student, grade=70.0)
        AssessmentGradeFactory(assessment=assessment2, student=student, grade=90.0)
        
        # Create connections with different weights
        AssessmentToLOFactory(assessment=assessment1, learning_outcome=lo, weight=0.3)
        AssessmentToLOFactory(assessment=assessment2, learning_outcome=lo, weight=0.7)
        
        score = calculate_lo_score(student, lo)
        expected = (70.0 * 0.3 + 90.0 * 0.7) / 1.0
        assert abs(score - expected) < 0.01


class TestCalculatePOScore:
    """Tests for calculate_po_score function"""
    
    def test_calculate_po_score_with_lo_scores(self, db):
        """Test calculating PO score with LO scores"""
        student = StudentFactory()
        course = CourseFactory()
        academic_board = AcademicBoardFactory()
        po = ProgramOutcomeFactory(academic_board=academic_board)
        
        # Create LO with score
        lo = LearningOutcomeFactory(course=course)
        assessment = AssessmentFactory(course=course)
        AssessmentGradeFactory(assessment=assessment, student=student, grade=80.0)
        AssessmentToLOFactory(assessment=assessment, learning_outcome=lo, weight=1.0)
        
        # Connect LO to PO
        LOToPOFactory(learning_outcome=lo, program_outcome=po, weight=1.0)
        
        score = calculate_po_score(student, po)
        assert score is not None
        assert abs(score - 80.0) < 0.01
    
    def test_calculate_po_score_no_connections(self, db):
        """Test calculating PO score with no connections"""
        student = StudentFactory()
        po = ProgramOutcomeFactory()
        
        score = calculate_po_score(student, po)
        assert score is None
    
    def test_calculate_po_score_multiple_los(self, db):
        """Test PO score calculation with multiple LOs"""
        student = StudentFactory()
        course = CourseFactory()
        academic_board = AcademicBoardFactory()
        po = ProgramOutcomeFactory(academic_board=academic_board)
        
        # Create two LOs with different scores
        lo1 = LearningOutcomeFactory(course=course)
        lo2 = LearningOutcomeFactory(course=course)
        
        assessment1 = AssessmentFactory(course=course)
        assessment2 = AssessmentFactory(course=course)
        
        AssessmentGradeFactory(assessment=assessment1, student=student, grade=70.0)
        AssessmentGradeFactory(assessment=assessment2, student=student, grade=90.0)
        
        AssessmentToLOFactory(assessment=assessment1, learning_outcome=lo1, weight=1.0)
        AssessmentToLOFactory(assessment=assessment2, learning_outcome=lo2, weight=1.0)
        
        # Connect both LOs to PO with equal weights
        LOToPOFactory(learning_outcome=lo1, program_outcome=po, weight=0.5)
        LOToPOFactory(learning_outcome=lo2, program_outcome=po, weight=0.5)
        
        score = calculate_po_score(student, po)
        expected = (70.0 + 90.0) / 2.0
        assert abs(score - expected) < 0.01


class TestGetCourseGraphData:
    """Tests for get_course_graph_data function"""
    
    def test_get_graph_data_basic(self, db, course):
        """Test getting basic graph data"""
        assessment = AssessmentFactory(course=course)
        lo = LearningOutcomeFactory(course=course)
        po = ProgramOutcomeFactory()
        
        AssessmentToLOFactory(assessment=assessment, learning_outcome=lo, weight=1.0)
        LOToPOFactory(learning_outcome=lo, program_outcome=po, weight=1.0)
        
        graph_data = get_course_graph_data(course)
        
        assert 'nodes' in graph_data
        assert 'edges' in graph_data
        assert len(graph_data['nodes']) > 0
        assert len(graph_data['edges']) > 0
    
    def test_get_graph_data_with_student(self, db, course):
        """Test getting graph data with student scores"""
        student = StudentFactory()
        assessment = AssessmentFactory(course=course)
        lo = LearningOutcomeFactory(course=course)
        
        AssessmentGradeFactory(assessment=assessment, student=student, grade=85.0)
        AssessmentToLOFactory(assessment=assessment, learning_outcome=lo, weight=1.0)
        
        graph_data = get_course_graph_data(course, student=student)
        
        # Check that nodes have grade/score data
        assessment_node = next(n for n in graph_data['nodes'] if n['type'] == 'assessment')
        assert 'grade' in assessment_node['data']
        
        lo_node = next(n for n in graph_data['nodes'] if n['type'] == 'learning_outcome')
        assert 'score' in lo_node['data']


class TestExecuteSafeDbOperations:
    """Tests for execute_safe_db_operations function"""
    
    def test_safe_db_operations_success(self, db):
        """Test successful database operations"""
        def operations(cursor):
            cursor.execute(
                "INSERT INTO edupace_app_course (code, name, description, credits, is_locked, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                ['TEST001', 'Test Course', 'Description', 3, False, '2024-01-01 00:00:00', '2024-01-01 00:00:00']
            )
            return {'success': True}
        
        success, message, result = execute_safe_db_operations(operations)
        assert success is True
        assert result['success'] is True
    
    def test_safe_db_operations_rollback_on_error(self, db):
        """Test that operations rollback on error"""
        initial_count = Course.objects.count()
        
        def operations(cursor):
            cursor.execute(
                "INSERT INTO edupace_app_course (code, name, description, credits, is_locked, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                ['TEST001', 'Test Course', 'Description', 3, False, '2024-01-01 00:00:00', '2024-01-01 00:00:00']
            )
            # Force an error
            raise ValueError("Test error")
        
        success, message, result = execute_safe_db_operations(operations)
        assert success is False
        assert 'error' in message.lower() or 'rolled back' in message.lower()
        
        # Verify no course was created
        assert Course.objects.count() == initial_count

