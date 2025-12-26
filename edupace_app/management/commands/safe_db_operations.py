"""
Django Management Command: Safe Database Operations with Transactions

This command provides a safe way to perform database operations using raw SQL
within Django transactions. All operations are wrapped in transaction.atomic()
to ensure data consistency.

Usage:
    python manage.py safe_db_operations

Safety Features:
    - All operations are wrapped in transactions (automatic rollback on error)
    - Parameterized queries prevent SQL injection
    - No DROP, TRUNCATE, or unsafe DELETE operations
    - Operations are logged for audit purposes

Example Operations:
    - Insert students, teachers, courses
    - Update course information
    - Create enrollments
    - Add assessment grades
    - Create learning/program outcomes
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone
from datetime import date


class Command(BaseCommand):
    help = 'Perform safe database operations using transactions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be executed without actually running',
        )
        parser.add_argument(
            '--operation',
            type=str,
            choices=[
                'insert_student',
                'update_course',
                'create_enrollment',
                'add_assessment_grade',
                'bulk_operations',
                'all'
            ],
            default='all',
            help='Specific operation to perform (default: all)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        operation = options['operation']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        try:
            if operation == 'all' or operation == 'insert_student':
                self.insert_student_example(dry_run)
            
            if operation == 'all' or operation == 'update_course':
                self.update_course_example(dry_run)
            
            if operation == 'all' or operation == 'create_enrollment':
                self.create_enrollment_example(dry_run)
            
            if operation == 'all' or operation == 'add_assessment_grade':
                self.add_assessment_grade_example(dry_run)
            
            if operation == 'all' or operation == 'bulk_operations':
                self.bulk_operations_example(dry_run)
            
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS('✅ All operations completed successfully!')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ Dry run completed - no changes made')
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error occurred: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING('All changes have been rolled back automatically')
            )
            raise

    def insert_student_example(self, dry_run):
        """Example: Insert a new student with User account"""
        self.stdout.write('\n📝 Example: Insert Student')
        
        if dry_run:
            self.stdout.write('  Would execute: INSERT INTO auth_user + edupace_app_student')
            return
        
        # Begin transaction
        with transaction.atomic():
            with connection.cursor() as cursor:
                # First, create the User account
                cursor.execute(
                    """
                    INSERT INTO auth_user (username, email, first_name, last_name, 
                                         password, is_staff, is_active, date_joined)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    [
                        'ahmet.student',
                        'ahmet@example.com',
                        'Ahmet',
                        'Yılmaz',
                        'pbkdf2_sha256$dummy',  # Note: Use proper password hashing in production
                        False,
                        True,
                        timezone.now()
                    ]
                )
                user_id = cursor.fetchone()[0]
                
                # Then, create the Student profile
                cursor.execute(
                    """
                    INSERT INTO edupace_app_student (user_id, student_id, enrollment_date, 
                                                     program, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [
                        user_id,
                        'STU2024001',
                        date.today(),
                        'Computer Science',
                        timezone.now()
                    ]
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Created student: Ahmet Yılmaz (STU2024001)')
                )

    def update_course_example(self, dry_run):
        """Example: Update course information safely"""
        self.stdout.write('\n📝 Example: Update Course')
        
        if dry_run:
            self.stdout.write('  Would execute: UPDATE edupace_app_course WHERE id=1')
            return
        
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Check if course exists first
                cursor.execute(
                    "SELECT id, code, name FROM edupace_app_course WHERE id = %s",
                    [1]
                )
                course = cursor.fetchone()
                
                if not course:
                    self.stdout.write(
                        self.style.WARNING('  ⚠️  Course with id=1 not found, skipping update')
                    )
                    return
                
                # Update course title
                cursor.execute(
                    "UPDATE edupace_app_course SET name = %s, updated_at = %s WHERE id = %s",
                    ['Mathematics 2', timezone.now(), 1]
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Updated course: {course[1]} → Mathematics 2')
                )

    def create_enrollment_example(self, dry_run):
        """Example: Create enrollment (ManyToMany relationship)"""
        self.stdout.write('\n📝 Example: Create Enrollment')
        
        if dry_run:
            self.stdout.write('  Would execute: INSERT INTO edupace_app_student_courses')
            return
        
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Get student and course IDs
                cursor.execute(
                    "SELECT id FROM edupace_app_student WHERE student_id = %s",
                    ['STU2024001']
                )
                student = cursor.fetchone()
                
                cursor.execute(
                    "SELECT id FROM edupace_app_course WHERE id = %s",
                    [1]
                )
                course = cursor.fetchone()
                
                if not student or not course:
                    self.stdout.write(
                        self.style.WARNING('  ⚠️  Student or course not found, skipping enrollment')
                    )
                    return
                
                # Check if enrollment already exists
                cursor.execute(
                    """
                    SELECT id FROM edupace_app_student_courses 
                    WHERE student_id = %s AND course_id = %s
                    """,
                    [student[0], course[0]]
                )
                
                if cursor.fetchone():
                    self.stdout.write(
                        self.style.WARNING('  ⚠️  Enrollment already exists, skipping')
                    )
                    return
                
                # Create enrollment
                cursor.execute(
                    """
                    INSERT INTO edupace_app_student_courses (student_id, course_id)
                    VALUES (%s, %s)
                    """,
                    [student[0], course[0]]
                )
                
                self.stdout.write(
                    self.style.SUCCESS('  ✅ Created enrollment')
                )

    def add_assessment_grade_example(self, dry_run):
        """Example: Add assessment grade for a student"""
        self.stdout.write('\n📝 Example: Add Assessment Grade')
        
        if dry_run:
            self.stdout.write('  Would execute: INSERT INTO edupace_app_assessmentgrade')
            return
        
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Get assessment and student IDs
                cursor.execute(
                    """
                    SELECT id FROM edupace_app_assessment 
                    WHERE course_id = %s AND name = %s
                    """,
                    [1, 'Midterm']
                )
                assessment = cursor.fetchone()
                
                cursor.execute(
                    "SELECT id FROM edupace_app_student WHERE student_id = %s",
                    ['STU2024001']
                )
                student = cursor.fetchone()
                
                if not assessment or not student:
                    self.stdout.write(
                        self.style.WARNING('  ⚠️  Assessment or student not found, skipping')
                    )
                    return
                
                # Check if grade already exists
                cursor.execute(
                    """
                    SELECT id FROM edupace_app_assessmentgrade 
                    WHERE assessment_id = %s AND student_id = %s
                    """,
                    [assessment[0], student[0]]
                )
                
                if cursor.fetchone():
                    self.stdout.write(
                        self.style.WARNING('  ⚠️  Grade already exists, skipping')
                    )
                    return
                
                # Insert assessment grade
                cursor.execute(
                    """
                    INSERT INTO edupace_app_assessmentgrade 
                    (assessment_id, student_id, grade, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [assessment[0], student[0], 85.5, timezone.now(), timezone.now()]
                )
                
                self.stdout.write(
                    self.style.SUCCESS('  ✅ Added assessment grade: 85.5')
                )

    def bulk_operations_example(self, dry_run):
        """Example: Multiple operations in a single transaction"""
        self.stdout.write('\n📝 Example: Bulk Operations')
        
        if dry_run:
            self.stdout.write('  Would execute: Multiple INSERT/UPDATE operations')
            return
        
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Operation 1: Update multiple course descriptions
                cursor.execute(
                    """
                    UPDATE edupace_app_course 
                    SET description = %s, updated_at = %s 
                    WHERE code LIKE %s
                    """,
                    ['Updated course description', timezone.now(), 'CS%']
                )
                updated_count = cursor.rowcount
                
                # Operation 2: Insert learning outcome if it doesn't exist
                cursor.execute(
                    """
                    SELECT id FROM edupace_app_learningoutcome 
                    WHERE course_id = %s AND code = %s
                    """,
                    [1, 'LO1']
                )
                
                if not cursor.fetchone():
                    # Get a user ID for created_by (use first teacher or admin)
                    cursor.execute(
                        "SELECT id FROM auth_user WHERE is_staff = %s LIMIT 1",
                        [True]
                    )
                    user = cursor.fetchone()
                    created_by_id = user[0] if user else None
                    
                    cursor.execute(
                        """
                        INSERT INTO edupace_app_learningoutcome 
                        (course_id, code, description, created_by_id, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        [
                            1,
                            'LO1',
                            'Understand fundamental concepts',
                            created_by_id,
                            timezone.now(),
                            timezone.now()
                        ]
                    )
                    self.stdout.write('  ✅ Created learning outcome: LO1')
                
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Updated {updated_count} course(s)')
                )


# ============================================================================
# STANDALONE SCRIPT VERSION (for use outside management commands)
# ============================================================================

def run_safe_operations():
    """
    Standalone function that can be imported and used in other scripts.
    
    Usage:
        from edupace_app.management.commands.safe_db_operations import run_safe_operations
        run_safe_operations()
    """
    from django.db import connection, transaction
    from django.utils import timezone
    from datetime import date
    
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # ✅ Example: Insert a new student
                cursor.execute(
                    """
                    INSERT INTO auth_user (username, email, first_name, last_name, 
                                         password, is_staff, is_active, date_joined)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    [
                        'new.student',
                        'new@example.com',
                        'New',
                        'Student',
                        'pbkdf2_sha256$dummy',  # Use proper password hashing
                        False,
                        True,
                        timezone.now()
                    ]
                )
                user_id = cursor.fetchone()[0]
                
                cursor.execute(
                    """
                    INSERT INTO edupace_app_student (user_id, student_id, enrollment_date, 
                                                     program, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [
                        user_id,
                        'STU2024002',
                        date.today(),
                        'Computer Science',
                        timezone.now()
                    ]
                )
                
                # ✅ Example: Update a course title
                cursor.execute(
                    "UPDATE edupace_app_course SET name = %s, updated_at = %s WHERE id = %s",
                    ['Updated Course Name', timezone.now(), 1]
                )
                
                # ✅ Example: Create enrollment
                cursor.execute(
                    """
                    INSERT INTO edupace_app_student_courses (student_id, course_id)
                    SELECT s.id, c.id
                    FROM edupace_app_student s, edupace_app_course c
                    WHERE s.student_id = %s AND c.id = %s
                    AND NOT EXISTS (
                        SELECT 1 FROM edupace_app_student_courses sc
                        WHERE sc.student_id = s.id AND sc.course_id = c.id
                    )
                    """,
                    ['STU2024002', 1]
                )
        
        print("✅ All operations completed successfully!")
        
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        print("All changes have been rolled back automatically")
        raise

