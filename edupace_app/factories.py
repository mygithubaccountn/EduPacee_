"""
Test factories for creating test data using factory_boy
"""
import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory
from faker import Faker

from edupace_app.models import (
    Student, Teacher, AcademicBoard, Course,
    ProgramOutcome, LearningOutcome, Grade,
    Assessment, AssessmentGrade, AssessmentToLO, LOToPO
)

fake = Faker()


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances"""
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')


class StudentFactory(DjangoModelFactory):
    """Factory for creating Student instances"""
    class Meta:
        model = Student
        django_get_or_create = ('student_id',)
    
    user = factory.SubFactory(UserFactory)
    student_id = factory.Sequence(lambda n: f'STU{n:03d}')
    enrollment_date = factory.Faker('date_object')
    program = factory.Faker('word')


class TeacherFactory(DjangoModelFactory):
    """Factory for creating Teacher instances"""
    class Meta:
        model = Teacher
        django_get_or_create = ('employee_id',)
    
    user = factory.SubFactory(UserFactory)
    employee_id = factory.Sequence(lambda n: f'TCH{n:03d}')
    department = factory.Faker('word')


class AcademicBoardFactory(DjangoModelFactory):
    """Factory for creating AcademicBoard instances"""
    class Meta:
        model = AcademicBoard
        django_get_or_create = ('employee_id',)
    
    user = factory.SubFactory(UserFactory)
    employee_id = factory.Sequence(lambda n: f'AB{n:03d}')
    designation = factory.Faker('job')


class CourseFactory(DjangoModelFactory):
    """Factory for creating Course instances"""
    class Meta:
        model = Course
        django_get_or_create = ('code',)
    
    code = factory.Sequence(lambda n: f'CS{n:03d}')
    name = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text', max_nb_chars=200)
    credits = factory.Faker('random_int', min=1, max=5)
    is_locked = False


class ProgramOutcomeFactory(DjangoModelFactory):
    """Factory for creating ProgramOutcome instances"""
    class Meta:
        model = ProgramOutcome
    
    academic_board = factory.SubFactory(AcademicBoardFactory)
    code = factory.Sequence(lambda n: f'PO{n}')
    description = factory.Faker('text', max_nb_chars=300)
    created_by = factory.LazyAttribute(lambda obj: obj.academic_board.user)


class LearningOutcomeFactory(DjangoModelFactory):
    """Factory for creating LearningOutcome instances"""
    class Meta:
        model = LearningOutcome
    
    course = factory.SubFactory(CourseFactory)
    code = factory.Sequence(lambda n: f'LO{n}')
    description = factory.Faker('text', max_nb_chars=300)
    created_by = factory.SubFactory(UserFactory)


class GradeFactory(DjangoModelFactory):
    """Factory for creating Grade instances"""
    class Meta:
        model = Grade
    
    student = factory.SubFactory(StudentFactory)
    course = factory.SubFactory(CourseFactory)
    grade = factory.Iterator(['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F'])
    percentage = factory.Faker('random_int', min=0, max=100)
    semester = factory.Faker('word')
    academic_year = factory.Faker('year')
    created_by = factory.SubFactory(UserFactory)


class AssessmentFactory(DjangoModelFactory):
    """Factory for creating Assessment instances"""
    class Meta:
        model = Assessment
    
    course = factory.SubFactory(CourseFactory)
    name = factory.Iterator(['Midterm', 'Final', 'Project', 'Quiz', 'Assignment'])
    weight_in_course = factory.Faker('random_int', min=10, max=50) / 100.0


class AssessmentGradeFactory(DjangoModelFactory):
    """Factory for creating AssessmentGrade instances"""
    class Meta:
        model = AssessmentGrade
    
    assessment = factory.SubFactory(AssessmentFactory)
    student = factory.SubFactory(StudentFactory)
    grade = factory.Faker('random_int', min=0, max=100)


class AssessmentToLOFactory(DjangoModelFactory):
    """Factory for creating AssessmentToLO instances"""
    class Meta:
        model = AssessmentToLO
    
    assessment = factory.SubFactory(AssessmentFactory)
    learning_outcome = factory.SubFactory(LearningOutcomeFactory)
    weight = factory.Faker('random_int', min=1, max=10) / 10.0


class LOToPOFactory(DjangoModelFactory):
    """Factory for creating LOToPO instances"""
    class Meta:
        model = LOToPO
    
    learning_outcome = factory.SubFactory(LearningOutcomeFactory)
    program_outcome = factory.SubFactory(ProgramOutcomeFactory)
    weight = factory.Faker('random_int', min=1, max=10) / 10.0

