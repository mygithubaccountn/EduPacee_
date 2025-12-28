"""
Unit tests for EduPace forms
"""
import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from edupace_app.forms import (
    RoleLoginForm, CourseForm, ProgramOutcomeForm,
    LearningOutcomeForm, GradeUploadForm, GradeForm,
    AssignTeacherToCourseForm, EnrollStudentToCourseForm,
    AssessmentForm, AssessmentGradeForm, AssessmentToLOForm, LOToPOForm
)
from edupace_app.models import Course, Student, Teacher, AcademicBoard
from edupace_app.factories import (
    CourseFactory, StudentFactory, TeacherFactory, AcademicBoardFactory,
    UserFactory
)


class TestRoleLoginForm:
    """Tests for RoleLoginForm"""
    
    def test_form_has_role_field(self, db):
        """Test that form has role field"""
        form = RoleLoginForm()
        assert 'role' in form.fields
        assert 'username' in form.fields
        assert 'password' in form.fields
    
    def test_form_role_choices(self, db):
        """Test role field has correct choices"""
        form = RoleLoginForm()
        role_choices = form.fields['role'].choices
        assert ('student', 'Student') in role_choices
        assert ('teacher', 'Teacher') in role_choices
        assert ('academic_board', 'Academic Board') in role_choices


class TestCourseForm:
    """Tests for CourseForm"""
    
    def test_course_form_fields(self, db):
        """Test that form has all required fields"""
        form = CourseForm()
        assert 'code' in form.fields
        assert 'name' in form.fields
        assert 'description' in form.fields
        assert 'credits' in form.fields
        assert 'is_locked' not in form.fields  # Should not be in form
    
    def test_course_form_valid_data(self, db):
        """Test form with valid data"""
        form_data = {
            'code': 'CS101',
            'name': 'Introduction to CS',
            'description': 'Basic CS concepts',
            'credits': 3
        }
        form = CourseForm(data=form_data)
        assert form.is_valid()
    
    def test_course_form_missing_required_fields(self, db):
        """Test form validation with missing fields"""
        form = CourseForm(data={})
        assert not form.is_valid()
        assert 'code' in form.errors
        assert 'name' in form.errors
        assert 'credits' in form.errors


class TestProgramOutcomeForm:
    """Tests for ProgramOutcomeForm"""
    
    def test_program_outcome_form_fields(self, db):
        """Test that form has required fields"""
        form = ProgramOutcomeForm()
        assert 'code' in form.fields
        assert 'description' in form.fields
    
    def test_program_outcome_form_valid_data(self, db):
        """Test form with valid data"""
        form_data = {
            'code': 'PO1',
            'description': 'Program outcome description'
        }
        form = ProgramOutcomeForm(data=form_data)
        assert form.is_valid()
    
    def test_program_outcome_form_missing_fields(self, db):
        """Test form validation with missing fields"""
        form = ProgramOutcomeForm(data={})
        assert not form.is_valid()
        assert 'code' in form.errors
        assert 'description' in form.errors


class TestLearningOutcomeForm:
    """Tests for LearningOutcomeForm"""
    
    def test_learning_outcome_form_fields(self, db):
        """Test that form has required fields"""
        form = LearningOutcomeForm()
        assert 'code' in form.fields
        assert 'description' in form.fields
    
    def test_learning_outcome_form_valid_data(self, db):
        """Test form with valid data"""
        form_data = {
            'code': 'LO1',
            'description': 'Learning outcome description'
        }
        form = LearningOutcomeForm(data=form_data)
        assert form.is_valid()


class TestGradeUploadForm:
    """Tests for GradeUploadForm"""
    
    def test_grade_upload_form_fields(self, db):
        """Test that form has required fields"""
        teacher = TeacherFactory()
        form = GradeUploadForm(teacher=teacher)
        assert 'excel_file' in form.fields
        assert 'course' in form.fields
        assert 'semester' in form.fields
        assert 'academic_year' in form.fields
    
    def test_grade_upload_form_course_queryset(self, db):
        """Test that course queryset is filtered by teacher"""
        teacher = TeacherFactory()
        course1 = CourseFactory()
        course2 = CourseFactory()
        teacher.courses.add(course1)
        
        form = GradeUploadForm(teacher=teacher)
        assert course1 in form.fields['course'].queryset
        assert course2 not in form.fields['course'].queryset
    
    def test_grade_upload_form_without_teacher(self, db):
        """Test form without teacher (should have empty course queryset)"""
        form = GradeUploadForm()
        assert form.fields['course'].queryset.count() == 0


class TestGradeForm:
    """Tests for GradeForm"""
    
    def test_grade_form_fields(self, db):
        """Test that form has required fields"""
        teacher = TeacherFactory()
        form = GradeForm(teacher=teacher)
        assert 'student' in form.fields
        assert 'course' in form.fields
        assert 'grade' in form.fields
        assert 'percentage' in form.fields
        assert 'semester' in form.fields
        assert 'academic_year' in form.fields
    
    def test_grade_form_course_queryset(self, db):
        """Test that course queryset is filtered by teacher"""
        teacher = TeacherFactory()
        course1 = CourseFactory()
        course2 = CourseFactory()
        teacher.courses.add(course1)
        
        form = GradeForm(teacher=teacher)
        assert course1 in form.fields['course'].queryset
        assert course2 not in form.fields['course'].queryset
    
    def test_grade_form_valid_data(self, db):
        """Test form with valid data"""
        student = StudentFactory()
        course = CourseFactory()
        teacher = TeacherFactory()
        teacher.courses.add(course)
        
        form_data = {
            'student': student.id,
            'course': course.id,
            'grade': 'A+',
            'percentage': 95.5,
            'semester': 'Fall 2024',
            'academic_year': '2024-2025'
        }
        form = GradeForm(data=form_data, teacher=teacher)
        assert form.is_valid()


class TestAssignTeacherToCourseForm:
    """Tests for AssignTeacherToCourseForm"""
    
    def test_assign_teacher_form_fields(self, db):
        """Test that form has required fields"""
        form = AssignTeacherToCourseForm()
        assert 'teacher' in form.fields
    
    def test_assign_teacher_form_valid_data(self, db):
        """Test form with valid data"""
        teacher = TeacherFactory()
        form_data = {'teacher': teacher.id}
        form = AssignTeacherToCourseForm(data=form_data)
        assert form.is_valid()


class TestEnrollStudentToCourseForm:
    """Tests for EnrollStudentToCourseForm"""
    
    def test_enroll_student_form_fields(self, db):
        """Test that form has required fields"""
        form = EnrollStudentToCourseForm()
        assert 'student' in form.fields
    
    def test_enroll_student_form_valid_data(self, db):
        """Test form with valid data"""
        student = StudentFactory()
        form_data = {'student': student.id}
        form = EnrollStudentToCourseForm(data=form_data)
        assert form.is_valid()


class TestAssessmentForm:
    """Tests for AssessmentForm"""
    
    def test_assessment_form_fields(self, db):
        """Test that form has required fields"""
        form = AssessmentForm()
        assert 'name' in form.fields
        assert 'weight_in_course' in form.fields
    
    def test_assessment_form_valid_data(self, db):
        """Test form with valid data"""
        form_data = {
            'name': 'Midterm',
            'weight_in_course': 0.3
        }
        form = AssessmentForm(data=form_data)
        assert form.is_valid()
    
    def test_assessment_form_weight_validation(self, db):
        """Test weight validation"""
        # Valid weight
        form_data = {'name': 'Midterm', 'weight_in_course': 0.3}
        form = AssessmentForm(data=form_data)
        assert form.is_valid()
        
        # Invalid weight (too high)
        form_data = {'name': 'Midterm', 'weight_in_course': 1.5}
        form = AssessmentForm(data=form_data)
        assert not form.is_valid()


class TestAssessmentGradeForm:
    """Tests for AssessmentGradeForm"""
    
    def test_assessment_grade_form_fields(self, db):
        """Test that form has required fields"""
        course = CourseFactory()
        form = AssessmentGradeForm(course=course)
        assert 'assessment' in form.fields
        assert 'student' in form.fields
        assert 'grade' in form.fields
    
    def test_assessment_grade_form_querysets(self, db):
        """Test that querysets are filtered by course"""
        course = CourseFactory()
        assessment1 = AssessmentFactory(course=course)
        assessment2 = AssessmentFactory()  # Different course
        student1 = StudentFactory()
        student2 = StudentFactory()
        course.students.add(student1)
        
        form = AssessmentGradeForm(course=course)
        assert assessment1 in form.fields['assessment'].queryset
        assert assessment2 not in form.fields['assessment'].queryset
        assert student1 in form.fields['student'].queryset
        assert student2 not in form.fields['student'].queryset
    
    def test_assessment_grade_form_valid_data(self, db):
        """Test form with valid data"""
        course = CourseFactory()
        assessment = AssessmentFactory(course=course)
        student = StudentFactory()
        course.students.add(student)
        
        form_data = {
            'assessment': assessment.id,
            'student': student.id,
            'grade': 85.5
        }
        form = AssessmentGradeForm(data=form_data, course=course)
        assert form.is_valid()


class TestAssessmentToLOForm:
    """Tests for AssessmentToLOForm"""
    
    def test_assessment_to_lo_form_fields(self, db):
        """Test that form has required fields"""
        course = CourseFactory()
        form = AssessmentToLOForm(course=course)
        assert 'assessment' in form.fields
        assert 'learning_outcome' in form.fields
        assert 'weight' in form.fields
    
    def test_assessment_to_lo_form_querysets(self, db):
        """Test that querysets are filtered by course"""
        course = CourseFactory()
        assessment1 = AssessmentFactory(course=course)
        assessment2 = AssessmentFactory()  # Different course
        lo1 = LearningOutcomeFactory(course=course)
        lo2 = LearningOutcomeFactory()  # Different course
        
        form = AssessmentToLOForm(course=course)
        assert assessment1 in form.fields['assessment'].queryset
        assert assessment2 not in form.fields['assessment'].queryset
        assert lo1 in form.fields['learning_outcome'].queryset
        assert lo2 not in form.fields['learning_outcome'].queryset


class TestLOToPOForm:
    """Tests for LOToPOForm"""
    
    def test_lo_to_po_form_fields(self, db):
        """Test that form has required fields"""
        course = CourseFactory()
        academic_board = AcademicBoardFactory()
        form = LOToPOForm(course=course, academic_board=academic_board)
        assert 'learning_outcome' in form.fields
        assert 'program_outcome' in form.fields
        assert 'weight' in form.fields
    
    def test_lo_to_po_form_querysets(self, db):
        """Test that querysets are filtered correctly"""
        course = CourseFactory()
        academic_board = AcademicBoardFactory()
        lo1 = LearningOutcomeFactory(course=course)
        lo2 = LearningOutcomeFactory()  # Different course
        po1 = ProgramOutcomeFactory(academic_board=academic_board)
        po2 = ProgramOutcomeFactory()  # Different board
        
        form = LOToPOForm(course=course, academic_board=academic_board)
        assert lo1 in form.fields['learning_outcome'].queryset
        assert lo2 not in form.fields['learning_outcome'].queryset
        assert po1 in form.fields['program_outcome'].queryset
        assert po2 not in form.fields['program_outcome'].queryset

