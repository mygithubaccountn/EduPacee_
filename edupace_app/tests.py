from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from .models import Course, Teacher, Student, LearningOutcome, Grade


class SmokeTest(TestCase):
    """Smoke test to verify the test suite runs correctly"""
    
    def test_basic_assertion(self):
        """Verify that basic test assertions work"""
        self.assertTrue(True)
        self.assertEqual(1 + 1, 2)


class ModelStrTests(TestCase):
    """Test model __str__ methods to ensure they work correctly"""
    
    def test_course_str(self):
        """Verify Course model __str__ returns expected format"""
        course = Course.objects.create(
            code='CS101',
            name='Introduction to Computer Science',
            credits=3
        )
        expected_str = 'CS101 - Introduction to Computer Science'
        self.assertEqual(str(course), expected_str)
    
    def test_course_str_with_minimal_data(self):
        """Verify Course __str__ works with minimal required fields"""
        course = Course.objects.create(
            code='MATH101',
            name='Calculus I',
            credits=4
        )
        self.assertIn('MATH101', str(course))
        self.assertIn('Calculus I', str(course))


class URLAvailabilityTests(TestCase):
    """Test that basic URLs are accessible (status 200 or 302)"""
    
    def test_login_url_exists(self):
        """Verify login page URL is accessible"""
        url = reverse('edupace_app:login')
        response = self.client.get(url)
        # Login page should return 200 (form) or 302 (if already logged in)
        self.assertIn(response.status_code, [200, 302])
    
    def test_dashboard_redirect_url_exists(self):
        """Verify dashboard redirect URL is accessible"""
        url = reverse('edupace_app:dashboard_redirect')
        response = self.client.get(url)
        # Dashboard redirect should return 302 (redirect) or 200
        self.assertIn(response.status_code, [200, 302])


class PermissionTests(TestCase):
    """Test role-based access control and permissions"""
    
    def setUp(self):
        """Create test users and course for permission testing"""
        # Create teacher user
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            password='testpass123',
            first_name='John',
            last_name='Teacher'
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='T001',
            department='Computer Science'
        )
        
        # Create student user
        self.student_user = User.objects.create_user(
            username='student1',
            password='testpass123',
            first_name='Jane',
            last_name='Student'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            student_id='S001',
            enrollment_date=date.today(),
            program='Computer Science'
        )
        
        # Create course and assign to teacher
        self.course = Course.objects.create(
            code='CS101',
            name='Introduction to Computer Science',
            credits=3
        )
        self.teacher.courses.add(self.course)
        self.student.courses.add(self.course)
    
    def test_anonymous_user_redirected_to_login(self):
        """Anonymous users should be redirected to login when accessing protected views"""
        url = reverse('edupace_app:teacher_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_student_cannot_access_teacher_dashboard(self):
        """Students should not be able to access teacher-only views"""
        self.client.login(username='student1', password='testpass123')
        url = reverse('edupace_app:teacher_dashboard')
        response = self.client.get(url)
        # Should redirect to dashboard_redirect or show error
        self.assertIn(response.status_code, [302, 403])
    
    def test_teacher_cannot_access_student_dashboard(self):
        """Teachers should not be able to access student-only views"""
        self.client.login(username='teacher1', password='testpass123')
        url = reverse('edupace_app:student_dashboard')
        response = self.client.get(url)
        # Should redirect to dashboard_redirect or show error
        self.assertIn(response.status_code, [302, 403])
    
    def test_teacher_can_access_own_course(self):
        """Teachers should be able to access courses they teach"""
        self.client.login(username='teacher1', password='testpass123')
        url = reverse('edupace_app:teacher_course_detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_teacher_cannot_access_unassigned_course(self):
        """Teachers should not access courses they don't teach"""
        # Create another course not assigned to teacher
        other_course = Course.objects.create(
            code='MATH101',
            name='Calculus I',
            credits=4
        )
        self.client.login(username='teacher1', password='testpass123')
        url = reverse('edupace_app:teacher_course_detail', args=[other_course.id])
        response = self.client.get(url)
        # Should redirect to teacher dashboard with error message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('edupace_app:teacher_dashboard'))
    
    def test_student_can_access_enrolled_course(self):
        """Students should be able to access courses they are enrolled in"""
        self.client.login(username='student1', password='testpass123')
        url = reverse('edupace_app:student_course_detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class ViewAccessTests(TestCase):
    """Test view behavior including redirects and HTTP status codes"""
    
    def setUp(self):
        """Create test users and course"""
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            password='testpass123',
            first_name='John',
            last_name='Teacher'
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='T001',
            department='Computer Science'
        )
        
        self.student_user = User.objects.create_user(
            username='student1',
            password='testpass123',
            first_name='Jane',
            last_name='Student'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            student_id='S001',
            enrollment_date=date.today(),
            program='Computer Science'
        )
        
        self.course = Course.objects.create(
            code='CS101',
            name='Introduction to Computer Science',
            credits=3
        )
        self.teacher.courses.add(self.course)
        self.student.courses.add(self.course)
    
    def test_login_page_accessible_anonymous(self):
        """Login page should be accessible to anonymous users"""
        url = reverse('edupace_app:login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_authenticated_user_redirected_from_login(self):
        """Authenticated users should be redirected from login page"""
        self.client.login(username='teacher1', password='testpass123')
        url = reverse('edupace_app:login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('edupace_app:dashboard_redirect'))
    
    def test_teacher_dashboard_returns_200(self):
        """Teacher dashboard should return 200 for authenticated teachers"""
        self.client.login(username='teacher1', password='testpass123')
        url = reverse('edupace_app:teacher_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_student_dashboard_returns_200(self):
        """Student dashboard should return 200 for authenticated students"""
        self.client.login(username='student1', password='testpass123')
        url = reverse('edupace_app:student_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_add_learning_outcome_requires_authentication(self):
        """Add learning outcome view should require authentication"""
        url = reverse('edupace_app:add_learning_outcome', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_add_learning_outcome_requires_teacher_role(self):
        """Add learning outcome should only be accessible to teachers"""
        self.client.login(username='student1', password='testpass123')
        url = reverse('edupace_app:add_learning_outcome', args=[self.course.id])
        response = self.client.get(url)
        # Should redirect or show forbidden
        self.assertIn(response.status_code, [302, 403])


class ModelViewInteractionTests(TestCase):
    """Test that models are created/not created based on permissions"""
    
    def setUp(self):
        """Create test users and course"""
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            password='testpass123',
            first_name='John',
            last_name='Teacher'
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='T001',
            department='Computer Science'
        )
        
        self.student_user = User.objects.create_user(
            username='student1',
            password='testpass123',
            first_name='Jane',
            last_name='Student'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            student_id='S001',
            enrollment_date=date.today(),
            program='Computer Science'
        )
        
        self.course = Course.objects.create(
            code='CS101',
            name='Introduction to Computer Science',
            credits=3
        )
        self.teacher.courses.add(self.course)
        self.student.courses.add(self.course)
    
    def test_teacher_can_create_learning_outcome(self):
        """Teachers should be able to create learning outcomes for their courses"""
        initial_count = LearningOutcome.objects.count()
        self.client.login(username='teacher1', password='testpass123')
        
        url = reverse('edupace_app:add_learning_outcome', args=[self.course.id])
        data = {
            'code': 'LO1',
            'description': 'Understand basic programming concepts'
        }
        response = self.client.post(url, data)
        
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        # Learning outcome should be created
        self.assertEqual(LearningOutcome.objects.count(), initial_count + 1)
        
        lo = LearningOutcome.objects.get(code='LO1', course=self.course)
        self.assertEqual(lo.description, 'Understand basic programming concepts')
        self.assertEqual(lo.created_by, self.teacher_user)
    
    def test_student_cannot_create_learning_outcome(self):
        """Students should not be able to create learning outcomes"""
        initial_count = LearningOutcome.objects.count()
        self.client.login(username='student1', password='testpass123')
        
        url = reverse('edupace_app:add_learning_outcome', args=[self.course.id])
        data = {
            'code': 'LO1',
            'description': 'Understand basic programming concepts'
        }
        response = self.client.post(url, data)
        
        # Should redirect or show forbidden
        self.assertIn(response.status_code, [302, 403])
        # Learning outcome should NOT be created
        self.assertEqual(LearningOutcome.objects.count(), initial_count)
    
    def test_teacher_cannot_create_learning_outcome_for_unassigned_course(self):
        """Teachers should not create learning outcomes for courses they don't teach"""
        other_course = Course.objects.create(
            code='MATH101',
            name='Calculus I',
            credits=4
        )
        initial_count = LearningOutcome.objects.count()
        self.client.login(username='teacher1', password='testpass123')
        
        url = reverse('edupace_app:add_learning_outcome', args=[other_course.id])
        data = {
            'code': 'LO1',
            'description': 'Understand calculus'
        }
        response = self.client.post(url, data)
        
        # Should redirect with error
        self.assertEqual(response.status_code, 302)
        # Learning outcome should NOT be created
        self.assertEqual(LearningOutcome.objects.count(), initial_count)
    
    def test_anonymous_cannot_create_learning_outcome(self):
        """Anonymous users should not be able to create learning outcomes"""
        initial_count = LearningOutcome.objects.count()
        
        url = reverse('edupace_app:add_learning_outcome', args=[self.course.id])
        data = {
            'code': 'LO1',
            'description': 'Understand basic programming concepts'
        }
        response = self.client.post(url, data)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
        # Learning outcome should NOT be created
        self.assertEqual(LearningOutcome.objects.count(), initial_count)


class RealisticScenarioTests(TestCase):
    """Test realistic scenarios a professor would expect in a university project"""
    
    def setUp(self):
        """Create realistic test scenario with multiple users and courses"""
        # Create teacher
        self.teacher_user = User.objects.create_user(
            username='prof.smith',
            password='testpass123',
            first_name='John',
            last_name='Smith'
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='PROF001',
            department='Computer Science'
        )
        
        # Create students
        self.student1_user = User.objects.create_user(
            username='student.alice',
            password='testpass123',
            first_name='Alice',
            last_name='Johnson'
        )
        self.student1 = Student.objects.create(
            user=self.student1_user,
            student_id='STU001',
            enrollment_date=date(2024, 1, 15),
            program='Computer Science'
        )
        
        self.student2_user = User.objects.create_user(
            username='student.bob',
            password='testpass123',
            first_name='Bob',
            last_name='Williams'
        )
        self.student2 = Student.objects.create(
            user=self.student2_user,
            student_id='STU002',
            enrollment_date=date(2024, 1, 15),
            program='Computer Science'
        )
        
        # Create courses
        self.cs101 = Course.objects.create(
            code='CS101',
            name='Introduction to Computer Science',
            credits=3,
            description='Basic programming and computer science concepts'
        )
        self.cs201 = Course.objects.create(
            code='CS201',
            name='Data Structures',
            credits=4,
            description='Advanced data structures and algorithms'
        )
        
        # Assign teacher to CS101 only
        self.teacher.courses.add(self.cs101)
        
        # Enroll students
        self.student1.courses.add(self.cs101, self.cs201)
        self.student2.courses.add(self.cs101)
    
    def test_teacher_manages_multiple_learning_outcomes(self):
        """Teacher should be able to add multiple learning outcomes to their course"""
        self.client.login(username='prof.smith', password='testpass123')
        
        # Add first learning outcome
        url = reverse('edupace_app:add_learning_outcome', args=[self.cs101.id])
        data1 = {
            'code': 'LO1',
            'description': 'Understand basic programming syntax'
        }
        response1 = self.client.post(url, data1)
        self.assertEqual(response1.status_code, 302)
        
        # Add second learning outcome
        data2 = {
            'code': 'LO2',
            'description': 'Apply programming concepts to solve problems'
        }
        response2 = self.client.post(url, data2)
        self.assertEqual(response2.status_code, 302)
        
        # Verify both learning outcomes exist
        los = LearningOutcome.objects.filter(course=self.cs101)
        self.assertEqual(los.count(), 2)
        self.assertTrue(los.filter(code='LO1').exists())
        self.assertTrue(los.filter(code='LO2').exists())
    
    def test_student_views_only_enrolled_courses(self):
        """Student should only see courses they are enrolled in"""
        self.client.login(username='student.alice', password='testpass123')
        
        # Student should see CS101
        url1 = reverse('edupace_app:student_course_detail', args=[self.cs101.id])
        response1 = self.client.get(url1)
        self.assertEqual(response1.status_code, 200)
        
        # Student should see CS201 (enrolled)
        url2 = reverse('edupace_app:student_course_detail', args=[self.cs201.id])
        response2 = self.client.get(url2)
        self.assertEqual(response2.status_code, 200)
    
    def test_teacher_sees_only_assigned_courses(self):
        """Teacher should only see courses they are assigned to"""
        self.client.login(username='prof.smith', password='testpass123')
        
        # Teacher should see CS101 (assigned)
        url1 = reverse('edupace_app:teacher_course_detail', args=[self.cs101.id])
        response1 = self.client.get(url1)
        self.assertEqual(response1.status_code, 200)
        
        # Teacher should NOT see CS201 (not assigned)
        url2 = reverse('edupace_app:teacher_course_detail', args=[self.cs201.id])
        response2 = self.client.get(url2)
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(response2.url, reverse('edupace_app:teacher_dashboard'))
    
    def test_learning_outcome_uniqueness_per_course(self):
        """Learning outcome codes should be unique per course - database enforces this"""
        self.client.login(username='prof.smith', password='testpass123')
        
        url = reverse('edupace_app:add_learning_outcome', args=[self.cs101.id])
        
        # Create first LO
        data1 = {
            'code': 'LO1',
            'description': 'First learning outcome'
        }
        response1 = self.client.post(url, data1)
        self.assertEqual(response1.status_code, 302)
        
        # Verify first LO was created
        self.assertTrue(LearningOutcome.objects.filter(course=self.cs101, code='LO1').exists())
        initial_count = LearningOutcome.objects.filter(course=self.cs101).count()
        
        # Try to create duplicate LO code in same course using direct model creation
        # This tests the database constraint directly
        from django.db import IntegrityError, transaction
        try:
            with transaction.atomic():
                LearningOutcome.objects.create(
                    course=self.cs101,
                    code='LO1',  # Duplicate code
                    description='Duplicate learning outcome',
                    created_by=self.teacher_user
                )
            # If we get here, the constraint didn't work (unexpected)
            self.fail("IntegrityError should have been raised for duplicate LO code")
        except IntegrityError:
            # Expected: database constraint prevents duplicate
            pass
        
        # Verify no duplicate was created (transaction was rolled back)
        final_count = LearningOutcome.objects.filter(course=self.cs101).count()
        self.assertEqual(final_count, initial_count)
        # Only one LO1 should exist
        lo1_count = LearningOutcome.objects.filter(course=self.cs101, code='LO1').count()
        self.assertEqual(lo1_count, 1)
