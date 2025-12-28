"""
Integration tests for CRUD operations in views
"""
import pytest
import pandas as pd
import tempfile
import os
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from edupace_app.factories import (
    CourseFactory, StudentFactory, TeacherFactory, AcademicBoardFactory,
    LearningOutcomeFactory, ProgramOutcomeFactory, GradeFactory,
    AssessmentFactory, AssessmentGradeFactory
)
from edupace_app.models import Course, LearningOutcome, ProgramOutcome, Grade


class TestAcademicBoardCourseCRUD:
    """Tests for Academic Board course CRUD operations"""
    
    def test_create_course(self, client, academic_board_user):
        """Test creating a course"""
        client.force_login(academic_board_user)
        response = client.post(reverse('edupace_app:create_course'), {
            'code': 'CS101',
            'name': 'Test Course',
            'description': 'Test Description',
            'credits': 3
        })
        assert response.status_code == 302  # Redirect after creation
        assert Course.objects.filter(code='CS101').exists()
    
    def test_edit_course(self, client, academic_board_user, course):
        """Test editing a course"""
        client.force_login(academic_board_user)
        response = client.post(reverse('edupace_app:edit_course', args=[course.id]), {
            'code': course.code,
            'name': 'Updated Course Name',
            'description': course.description,
            'credits': course.credits
        })
        assert response.status_code == 302
        course.refresh_from_db()
        assert course.name == 'Updated Course Name'
    
    def test_delete_course(self, client, academic_board_user, course):
        """Test deleting a course"""
        client.force_login(academic_board_user)
        course_id = course.id
        response = client.post(reverse('edupace_app:delete_course', args=[course.id]))
        assert response.status_code == 302
        assert not Course.objects.filter(id=course_id).exists()
    
    def test_teacher_cannot_create_course(self, client, teacher_user):
        """Test that teachers cannot create courses"""
        client.force_login(teacher_user)
        response = client.get(reverse('edupace_app:create_course'))
        assert response.status_code == 302  # Redirect (permission denied)


class TestProgramOutcomeCRUD:
    """Tests for Program Outcome CRUD operations"""
    
    def test_create_program_outcome(self, client, academic_board_user, course):
        """Test creating a program outcome"""
        client.force_login(academic_board_user)
        board = academic_board_user.academic_board_profile
        response = client.post(reverse('edupace_app:add_program_outcome', args=[course.id]), {
            'code': 'PO1',
            'description': 'Program Outcome 1'
        })
        assert response.status_code == 302
        assert ProgramOutcome.objects.filter(code='PO1', academic_board=board).exists()
    
    def test_edit_program_outcome(self, client, academic_board_user):
        """Test editing a program outcome"""
        board = academic_board_user.academic_board_profile
        po = ProgramOutcomeFactory(academic_board=board, code='PO1')
        client.force_login(academic_board_user)
        response = client.post(reverse('edupace_app:edit_program_outcome', args=[po.id]), {
            'code': 'PO1',
            'description': 'Updated Description'
        })
        assert response.status_code == 302
        po.refresh_from_db()
        assert po.description == 'Updated Description'
    
    def test_delete_program_outcome(self, client, academic_board_user):
        """Test deleting a program outcome"""
        board = academic_board_user.academic_board_profile
        po = ProgramOutcomeFactory(academic_board=board)
        po_id = po.id
        client.force_login(academic_board_user)
        response = client.post(reverse('edupace_app:delete_program_outcome', args=[po.id]))
        assert response.status_code == 302
        assert not ProgramOutcome.objects.filter(id=po_id).exists()


class TestLearningOutcomeCRUD:
    """Tests for Learning Outcome CRUD operations"""
    
    def test_create_learning_outcome(self, client, teacher_user, course):
        """Test creating a learning outcome"""
        teacher_user.teacher_profile.courses.add(course)
        client.force_login(teacher_user)
        response = client.post(reverse('edupace_app:add_learning_outcome', args=[course.id]), {
            'code': 'LO1',
            'description': 'Learning Outcome 1'
        })
        assert response.status_code == 302
        assert LearningOutcome.objects.filter(code='LO1', course=course).exists()
    
    def test_teacher_cannot_add_lo_to_unassigned_course(self, client, teacher_user, course):
        """Test that teachers cannot add LO to unassigned course"""
        client.force_login(teacher_user)
        response = client.post(reverse('edupace_app:add_learning_outcome', args=[course.id]), {
            'code': 'LO1',
            'description': 'Learning Outcome 1'
        })
        assert response.status_code == 302  # Redirect (permission denied)
        assert not LearningOutcome.objects.filter(code='LO1', course=course).exists()
    
    def test_teacher_cannot_add_lo_to_locked_course(self, client, teacher_user, locked_course):
        """Test that teachers cannot add LO to locked course"""
        teacher_user.teacher_profile.courses.add(locked_course)
        client.force_login(teacher_user)
        response = client.post(reverse('edupace_app:add_learning_outcome', args=[locked_course.id]), {
            'code': 'LO1',
            'description': 'Learning Outcome 1'
        })
        assert response.status_code == 302  # Redirect (permission denied)
        assert not LearningOutcome.objects.filter(code='LO1', course=locked_course).exists()
    
    def test_edit_learning_outcome(self, client, teacher_user, course):
        """Test editing a learning outcome"""
        teacher_user.teacher_profile.courses.add(course)
        lo = LearningOutcomeFactory(course=course)
        client.force_login(teacher_user)
        response = client.post(reverse('edupace_app:edit_learning_outcome', args=[lo.id]), {
            'code': lo.code,
            'description': 'Updated Description'
        })
        assert response.status_code == 302
        lo.refresh_from_db()
        assert lo.description == 'Updated Description'
    
    def test_delete_learning_outcome(self, client, teacher_user, course):
        """Test deleting a learning outcome"""
        teacher_user.teacher_profile.courses.add(course)
        lo = LearningOutcomeFactory(course=course)
        lo_id = lo.id
        client.force_login(teacher_user)
        response = client.post(reverse('edupace_app:delete_learning_outcome', args=[lo.id]))
        assert response.status_code == 302
        assert not LearningOutcome.objects.filter(id=lo_id).exists()


class TestGradeOperations:
    """Tests for grade operations"""
    
    def test_upload_grades_excel(self, client, teacher_user, course):
        """Test uploading grades via Excel"""
        teacher_user.teacher_profile.courses.add(course)
        student = StudentFactory()
        
        # Create Excel file
        df = pd.DataFrame({
            'Student ID': [student.student_id],
            'Grade': ['A+'],
            'Percentage': [95.5]
        })
        
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.xlsx', delete=False) as f:
            df.to_excel(f.name, index=False)
            f.seek(0)
            excel_file = SimpleUploadedFile(
                name='grades.xlsx',
                content=open(f.name, 'rb').read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            client.force_login(teacher_user)
            response = client.post(reverse('edupace_app:upload_grades', args=[course.id]), {
                'excel_file': excel_file,
                'course': course.id,
                'semester': 'Fall 2024',
                'academic_year': '2024-2025'
            })
            
            os.unlink(f.name)
        
        assert response.status_code == 302  # Redirect after upload
        assert Grade.objects.filter(student=student, course=course).exists()
    
    def test_teacher_cannot_upload_grades_to_locked_course(self, client, teacher_user, locked_course):
        """Test that teachers cannot upload grades to locked course"""
        teacher_user.teacher_profile.courses.add(locked_course)
        student = StudentFactory()
        
        df = pd.DataFrame({
            'Student ID': [student.student_id],
            'Grade': ['A+']
        })
        
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.xlsx', delete=False) as f:
            df.to_excel(f.name, index=False)
            f.seek(0)
            excel_file = SimpleUploadedFile(
                name='grades.xlsx',
                content=open(f.name, 'rb').read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            client.force_login(teacher_user)
            response = client.post(reverse('edupace_app:upload_grades', args=[locked_course.id]), {
                'excel_file': excel_file,
                'course': locked_course.id
            })
            
            os.unlink(f.name)
        
        assert response.status_code == 302  # Redirect (permission denied)
        assert not Grade.objects.filter(student=student, course=locked_course).exists()


class TestCourseEnrollment:
    """Tests for course enrollment operations"""
    
    def test_enroll_student_to_course(self, client, academic_board_user, course):
        """Test enrolling a student to a course"""
        student = StudentFactory()
        client.force_login(academic_board_user)
        response = client.post(reverse('edupace_app:enroll_student', args=[course.id]), {
            'student': student.id
        })
        assert response.status_code == 302
        assert course in student.courses.all()
    
    def test_assign_teacher_to_course(self, client, academic_board_user, course):
        """Test assigning a teacher to a course"""
        teacher = TeacherFactory()
        client.force_login(academic_board_user)
        response = client.post(reverse('edupace_app:assign_teacher', args=[course.id]), {
            'teacher': teacher.id
        })
        assert response.status_code == 302
        assert course in teacher.courses.all()


class TestStudentViews:
    """Tests for student-specific views"""
    
    def test_student_course_detail(self, client, student_user, course):
        """Test student viewing course details"""
        student_user.student_profile.courses.add(course)
        client.force_login(student_user)
        response = client.get(reverse('edupace_app:student_course_detail', args=[course.id]))
        assert response.status_code == 200
        assert 'course' in response.context
    
    def test_student_cannot_view_unenrolled_course(self, client, student_user, course):
        """Test that students cannot view unenrolled courses"""
        client.force_login(student_user)
        response = client.get(reverse('edupace_app:student_course_detail', args=[course.id]))
        assert response.status_code == 302  # Redirect (not enrolled)
    
    def test_student_dashboard_shows_enrolled_courses(self, client, student_user, course):
        """Test that student dashboard shows enrolled courses"""
        student_user.student_profile.courses.add(course)
        client.force_login(student_user)
        response = client.get(reverse('edupace_app:student_dashboard'))
        assert response.status_code == 200
        assert course in response.context['courses']


class TestTeacherViews:
    """Tests for teacher-specific views"""
    
    def test_teacher_course_detail(self, client, teacher_user, course):
        """Test teacher viewing course details"""
        teacher_user.teacher_profile.courses.add(course)
        client.force_login(teacher_user)
        response = client.get(reverse('edupace_app:teacher_course_detail', args=[course.id]))
        assert response.status_code == 200
        assert 'course' in response.context
    
    def test_teacher_cannot_view_unassigned_course(self, client, teacher_user, course):
        """Test that teachers cannot view unassigned courses"""
        client.force_login(teacher_user)
        response = client.get(reverse('edupace_app:teacher_course_detail', args=[course.id]))
        assert response.status_code == 302  # Redirect (not assigned)
    
    def test_teacher_dashboard_shows_assigned_courses(self, client, teacher_user, course):
        """Test that teacher dashboard shows assigned courses"""
        teacher_user.teacher_profile.courses.add(course)
        client.force_login(teacher_user)
        response = client.get(reverse('edupace_app:teacher_dashboard'))
        assert response.status_code == 200
        assert course in response.context['courses']

