"""
Unit tests for EduPace models
"""
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth.models import User

from edupace_app.models import (
    Course, Student, Teacher, AcademicBoard,
    ProgramOutcome, LearningOutcome, Grade,
    Assessment, AssessmentGrade, AssessmentToLO, LOToPO
)
from edupace_app.factories import (
    CourseFactory, StudentFactory, TeacherFactory, AcademicBoardFactory,
    ProgramOutcomeFactory, LearningOutcomeFactory, GradeFactory,
    AssessmentFactory, AssessmentGradeFactory, AssessmentToLOFactory, LOToPOFactory
)


class TestCourse:
    """Tests for Course model"""
    
    def test_course_creation(self, db):
        """Test creating a course"""
        course = CourseFactory()
        assert course.code is not None
        assert course.name is not None
        assert course.credits >= 1
        assert course.credits <= 10
        assert course.is_locked is False
    
    def test_course_str(self, db):
        """Test course string representation"""
        course = CourseFactory(code='CS101', name='Test Course')
        assert str(course) == 'CS101 - Test Course'
    
    def test_course_unique_code(self, db):
        """Test that course codes must be unique"""
        CourseFactory(code='CS101')
        with pytest.raises(IntegrityError):
            CourseFactory(code='CS101')
    
    def test_course_credits_validation(self, db):
        """Test credits validation"""
        # Valid credits
        course = CourseFactory(credits=3)
        assert course.credits == 3
        
        # Test minimum validator (should be enforced at model level)
        with pytest.raises(ValidationError):
            course = Course(code='CS999', name='Test', credits=0)
            course.full_clean()
    
    def test_course_ordering(self, db):
        """Test that courses are ordered by code"""
        CourseFactory(code='CS200')
        CourseFactory(code='CS100')
        CourseFactory(code='CS300')
        
        courses = Course.objects.all()
        assert courses[0].code == 'CS100'
        assert courses[1].code == 'CS200'
        assert courses[2].code == 'CS300'


class TestStudent:
    """Tests for Student model"""
    
    def test_student_creation(self, db):
        """Test creating a student"""
        student = StudentFactory()
        assert student.student_id is not None
        assert student.user is not None
        assert hasattr(student.user, 'student_profile')
    
    def test_student_str(self, db):
        """Test student string representation"""
        student = StudentFactory(student_id='STU001')
        assert 'STU001' in str(student)
    
    def test_student_unique_id(self, db):
        """Test that student IDs must be unique"""
        StudentFactory(student_id='STU001')
        with pytest.raises(IntegrityError):
            StudentFactory(student_id='STU001')
    
    def test_student_courses_relationship(self, db):
        """Test student-course many-to-many relationship"""
        student = StudentFactory()
        course1 = CourseFactory()
        course2 = CourseFactory()
        
        student.courses.add(course1, course2)
        assert student.courses.count() == 2
        assert course1 in student.courses.all()
        assert course2 in student.courses.all()


class TestTeacher:
    """Tests for Teacher model"""
    
    def test_teacher_creation(self, db):
        """Test creating a teacher"""
        teacher = TeacherFactory()
        assert teacher.employee_id is not None
        assert teacher.user is not None
        assert hasattr(teacher.user, 'teacher_profile')
    
    def test_teacher_str(self, db):
        """Test teacher string representation"""
        teacher = TeacherFactory(employee_id='TCH001')
        assert 'TCH001' in str(teacher)
    
    def test_teacher_unique_id(self, db):
        """Test that employee IDs must be unique"""
        TeacherFactory(employee_id='TCH001')
        with pytest.raises(IntegrityError):
            TeacherFactory(employee_id='TCH001')
    
    def test_teacher_courses_relationship(self, db):
        """Test teacher-course many-to-many relationship"""
        teacher = TeacherFactory()
        course1 = CourseFactory()
        course2 = CourseFactory()
        
        teacher.courses.add(course1, course2)
        assert teacher.courses.count() == 2


class TestAcademicBoard:
    """Tests for AcademicBoard model"""
    
    def test_academic_board_creation(self, db):
        """Test creating an academic board member"""
        board = AcademicBoardFactory()
        assert board.employee_id is not None
        assert board.user is not None
        assert hasattr(board.user, 'academic_board_profile')
    
    def test_academic_board_str(self, db):
        """Test academic board string representation"""
        board = AcademicBoardFactory(employee_id='AB001')
        assert 'AB001' in str(board)


class TestProgramOutcome:
    """Tests for ProgramOutcome model"""
    
    def test_program_outcome_creation(self, db):
        """Test creating a program outcome"""
        po = ProgramOutcomeFactory()
        assert po.code is not None
        assert po.description is not None
        assert po.academic_board is not None
    
    def test_program_outcome_str(self, db):
        """Test program outcome string representation"""
        po = ProgramOutcomeFactory(code='PO1')
        assert str(po) == 'PO1'
    
    def test_program_outcome_unique_per_board(self, db):
        """Test that PO codes must be unique per academic board"""
        board = AcademicBoardFactory()
        ProgramOutcomeFactory(academic_board=board, code='PO1')
        
        # Same code for different board should work
        board2 = AcademicBoardFactory()
        ProgramOutcomeFactory(academic_board=board2, code='PO1')
        
        # Same code for same board should fail
        with pytest.raises(IntegrityError):
            ProgramOutcomeFactory(academic_board=board, code='PO1')


class TestLearningOutcome:
    """Tests for LearningOutcome model"""
    
    def test_learning_outcome_creation(self, db):
        """Test creating a learning outcome"""
        lo = LearningOutcomeFactory()
        assert lo.code is not None
        assert lo.description is not None
        assert lo.course is not None
    
    def test_learning_outcome_str(self, db):
        """Test learning outcome string representation"""
        course = CourseFactory(code='CS101')
        lo = LearningOutcomeFactory(course=course, code='LO1')
        assert str(lo) == 'CS101 - LO1'
    
    def test_learning_outcome_unique_per_course(self, db):
        """Test that LO codes must be unique per course"""
        course = CourseFactory()
        LearningOutcomeFactory(course=course, code='LO1')
        
        # Same code for different course should work
        course2 = CourseFactory()
        LearningOutcomeFactory(course=course2, code='LO1')
        
        # Same code for same course should fail
        with pytest.raises(IntegrityError):
            LearningOutcomeFactory(course=course, code='LO1')


class TestGrade:
    """Tests for Grade model"""
    
    def test_grade_creation(self, db):
        """Test creating a grade"""
        grade = GradeFactory()
        assert grade.grade in [choice[0] for choice in Grade.GRADE_CHOICES]
        assert grade.student is not None
        assert grade.course is not None
    
    def test_grade_str(self, db):
        """Test grade string representation"""
        student = StudentFactory(student_id='STU001')
        course = CourseFactory(code='CS101')
        grade = GradeFactory(student=student, course=course, grade='A+')
        assert 'STU001' in str(grade)
        assert 'CS101' in str(grade)
        assert 'A+' in str(grade)
    
    def test_grade_choices(self, db):
        """Test valid grade choices"""
        valid_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F']
        for grade_value in valid_grades:
            grade = GradeFactory(grade=grade_value)
            assert grade.grade == grade_value
    
    def test_grade_percentage_validation(self, db):
        """Test percentage validation"""
        # Valid percentage
        grade = GradeFactory(percentage=85.5)
        assert grade.percentage == 85.5
        
        # Test percentage range (should be enforced at model level)
        with pytest.raises(ValidationError):
            grade = GradeFactory.build(percentage=150.0)
            grade.full_clean()
    
    def test_grade_unique_per_student_course_semester(self, db):
        """Test that grades are unique per student/course/semester/year"""
        student = StudentFactory()
        course = CourseFactory()
        semester = 'Fall 2024'
        year = '2024-2025'
        
        GradeFactory(student=student, course=course, semester=semester, academic_year=year)
        
        # Same combination should fail
        with pytest.raises(IntegrityError):
            GradeFactory(student=student, course=course, semester=semester, academic_year=year)


class TestAssessment:
    """Tests for Assessment model"""
    
    def test_assessment_creation(self, db):
        """Test creating an assessment"""
        assessment = AssessmentFactory()
        assert assessment.name is not None
        assert assessment.course is not None
        assert 0.0 <= assessment.weight_in_course <= 1.0
    
    def test_assessment_str(self, db):
        """Test assessment string representation"""
        course = CourseFactory(code='CS101')
        assessment = AssessmentFactory(course=course, name='Midterm')
        assert str(assessment) == 'CS101 - Midterm'
    
    def test_assessment_unique_per_course(self, db):
        """Test that assessment names must be unique per course"""
        course = CourseFactory()
        AssessmentFactory(course=course, name='Midterm')
        
        # Same name for different course should work
        course2 = CourseFactory()
        AssessmentFactory(course=course2, name='Midterm')
        
        # Same name for same course should fail
        with pytest.raises(IntegrityError):
            AssessmentFactory(course=course, name='Midterm')
    
    def test_assessment_weight_validation(self, db):
        """Test weight validation"""
        # Valid weight
        assessment = AssessmentFactory(weight_in_course=0.3)
        assert assessment.weight_in_course == 0.3
        
        # Test weight range (should be enforced at model level)
        with pytest.raises(ValidationError):
            assessment = AssessmentFactory.build(weight_in_course=1.5)
            assessment.full_clean()


class TestAssessmentGrade:
    """Tests for AssessmentGrade model"""
    
    def test_assessment_grade_creation(self, db):
        """Test creating an assessment grade"""
        ag = AssessmentGradeFactory()
        assert ag.assessment is not None
        assert ag.student is not None
        assert 0.0 <= ag.grade <= 100.0
    
    def test_assessment_grade_str(self, db):
        """Test assessment grade string representation"""
        student = StudentFactory(student_id='STU001')
        assessment = AssessmentFactory(name='Midterm')
        ag = AssessmentGradeFactory(student=student, assessment=assessment, grade=85.5)
        assert 'STU001' in str(ag)
        assert 'Midterm' in str(ag)
        assert '85.5' in str(ag)
    
    def test_assessment_grade_unique_per_student_assessment(self, db):
        """Test that assessment grades are unique per student/assessment"""
        student = StudentFactory()
        assessment = AssessmentFactory()
        
        AssessmentGradeFactory(student=student, assessment=assessment)
        
        # Same combination should fail
        with pytest.raises(IntegrityError):
            AssessmentGradeFactory(student=student, assessment=assessment)


class TestAssessmentToLO:
    """Tests for AssessmentToLO model"""
    
    def test_assessment_to_lo_creation(self, db):
        """Test creating an assessment to LO connection"""
        atl = AssessmentToLOFactory()
        assert atl.assessment is not None
        assert atl.learning_outcome is not None
        assert atl.weight >= 0.0
    
    def test_assessment_to_lo_str(self, db):
        """Test assessment to LO string representation"""
        assessment = AssessmentFactory(name='Midterm')
        lo = LearningOutcomeFactory(code='LO1')
        atl = AssessmentToLOFactory(assessment=assessment, learning_outcome=lo, weight=0.6)
        assert 'Midterm' in str(atl)
        assert 'LO1' in str(atl)
        assert '0.6' in str(atl)
    
    def test_assessment_to_lo_unique(self, db):
        """Test that assessment-LO connections are unique"""
        assessment = AssessmentFactory()
        lo = LearningOutcomeFactory()
        
        AssessmentToLOFactory(assessment=assessment, learning_outcome=lo)
        
        # Same combination should fail
        with pytest.raises(IntegrityError):
            AssessmentToLOFactory(assessment=assessment, learning_outcome=lo)


class TestLOToPO:
    """Tests for LOToPO model"""
    
    def test_lo_to_po_creation(self, db):
        """Test creating an LO to PO connection"""
        ltp = LOToPOFactory()
        assert ltp.learning_outcome is not None
        assert ltp.program_outcome is not None
        assert ltp.weight >= 0.0
    
    def test_lo_to_po_str(self, db):
        """Test LO to PO string representation"""
        lo = LearningOutcomeFactory(code='LO1')
        po = ProgramOutcomeFactory(code='PO1')
        ltp = LOToPOFactory(learning_outcome=lo, program_outcome=po, weight=1.0)
        assert 'LO1' in str(ltp)
        assert 'PO1' in str(ltp)
        assert '1.0' in str(ltp)
    
    def test_lo_to_po_unique(self, db):
        """Test that LO-PO connections are unique"""
        lo = LearningOutcomeFactory()
        po = ProgramOutcomeFactory()
        
        LOToPOFactory(learning_outcome=lo, program_outcome=po)
        
        # Same combination should fail
        with pytest.raises(IntegrityError):
            LOToPOFactory(learning_outcome=lo, program_outcome=po)

