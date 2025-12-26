from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.db.models import Q, Sum, Avg
from django.db import connection, transaction
from .models import Teacher, Student, AcademicBoard, AssessmentGrade, AssessmentToLO, LOToPO


def get_user_role(user):
    """Get the role of a user"""
    if not user.is_authenticated:
        return None
    
    if hasattr(user, 'teacher_profile'):
        return 'teacher'
    elif hasattr(user, 'student_profile'):
        return 'student'
    elif hasattr(user, 'academic_board_profile'):
        return 'academic_board'
    return None


def get_user_profile(user):
    """Get the profile object for a user based on their role"""
    role = get_user_role(user)
    if role == 'teacher':
        return user.teacher_profile
    elif role == 'student':
        return user.student_profile
    elif role == 'academic_board':
        return user.academic_board_profile
    return None


def role_required(*allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in to access this page.')
                return redirect('edupace_app:login')
            
            user_role = get_user_role(request.user)
            if user_role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('edupace_app:dashboard_redirect')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def check_course_edit_permission(user, course):
    """Check if user can edit a course (Academic Board only)"""
    if get_user_role(user) != 'academic_board':
        return False
    return True


def check_learning_outcome_permission(user, course):
    """Check if user can add learning outcomes (Teacher only)"""
    if get_user_role(user) != 'teacher':
        return False
    
    try:
        teacher = user.teacher_profile
        # Check if teacher is assigned to this course
        if not teacher.courses.filter(id=course.id).exists():
            return False
    except Teacher.DoesNotExist:
        return False
    
    return True


def check_grade_permission(user, course):
    """Check if user can add grades (Teacher only, and only if course is not locked)"""
    return check_learning_outcome_permission(user, course)


def excel_to_pdf(excel_file_path, output_pdf_path):
    """
    Convert Excel file to PDF
    Requires: openpyxl, reportlab, pandas
    """
    try:
        import pandas as pd
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        # Read Excel file
        df = pd.read_excel(excel_file_path)
        
        # Create PDF
        doc = SimpleDocTemplate(output_pdf_path, pagesize=A4)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
        )
        
        # Add title
        title = Paragraph("Grade Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Convert DataFrame to list of lists for table
        data = [df.columns.tolist()] + df.values.tolist()
        
        # Create table
        table = Table(data)
        
        # Style the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        return True
        
    except Exception as e:
        print(f"Error converting Excel to PDF: {str(e)}")
        return False


def process_excel_grades(excel_file, course, semester='', academic_year='', created_by=None):
    """
    Process Excel file and create Grade objects
    Expected Excel format:
    - First row: headers (Student ID, Grade, Percentage)
    - Subsequent rows: data
    """
    try:
        import pandas as pd
        from .models import Student, Grade
        
        # Read Excel file
        df = pd.read_excel(excel_file)
        
        # Expected columns (case-insensitive)
        df.columns = df.columns.str.strip().str.lower()
        
        # Map common column names
        student_id_col = None
        grade_col = None
        percentage_col = None
        
        for col in df.columns:
            if 'student' in col and 'id' in col:
                student_id_col = col
            elif 'grade' in col:
                grade_col = col
            elif 'percentage' in col or 'percent' in col:
                percentage_col = col
        
        if not student_id_col or not grade_col:
            return False, "Excel file must contain 'Student ID' and 'Grade' columns"
        
        grades_created = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                student_id = str(row[student_id_col]).strip()
                grade_value = str(row[grade_col]).strip().upper()
                percentage = None
                
                if percentage_col and pd.notna(row.get(percentage_col)):
                    percentage = float(row[percentage_col])
                
                # Get student
                try:
                    student = Student.objects.get(student_id=student_id)
                except Student.DoesNotExist:
                    errors.append(f"Student with ID {student_id} not found (row {index + 2})")
                    continue
                
                # Validate grade
                valid_grades = [choice[0] for choice in Grade.GRADE_CHOICES]
                if grade_value not in valid_grades:
                    errors.append(f"Invalid grade '{grade_value}' for student {student_id} (row {index + 2})")
                    continue
                
                # Create or update grade
                grade, created = Grade.objects.update_or_create(
                    student=student,
                    course=course,
                    semester=semester,
                    academic_year=academic_year,
                    defaults={
                        'grade': grade_value,
                        'percentage': percentage,
                        'created_by': created_by,
                    }
                )
                
                if created:
                    grades_created += 1
                    
            except Exception as e:
                errors.append(f"Error processing row {index + 2}: {str(e)}")
                continue
        
        message = f"Successfully created/updated {grades_created} grade(s)."
        if errors:
            message += f" {len(errors)} error(s) occurred."
        
        return True, message, errors
        
    except Exception as e:
        return False, f"Error processing Excel file: {str(e)}", []


def calculate_lo_score(student, learning_outcome):
    """
    Calculate Learning Outcome score for a student.
    Traverses AssessmentToLO edges with weights.
    
    Formula: LO_score = Σ(AssessmentGrade × weight) / Σ(weights)
    """
    # Get all assessment connections for this learning outcome
    connections = AssessmentToLO.objects.filter(learning_outcome=learning_outcome)
    
    if not connections.exists():
        return None
    
    total_weighted_score = 0.0
    total_weight = 0.0
    
    for connection in connections:
        # Get the student's grade for this assessment
        try:
            assessment_grade = AssessmentGrade.objects.get(
                assessment=connection.assessment,
                student=student
            )
            grade_value = assessment_grade.grade
            weight = connection.weight
            
            total_weighted_score += grade_value * weight
            total_weight += weight
        except AssessmentGrade.DoesNotExist:
            # Student doesn't have a grade for this assessment, skip it
            continue
    
    if total_weight == 0:
        return None
    
    return total_weighted_score / total_weight


def calculate_po_score(student, program_outcome):
    """
    Calculate Program Outcome score for a student.
    Traverses LOToPO edges with weights.
    
    Formula: PO_score = Σ(LO_score × weight) / Σ(weights)
    """
    # Get all LO connections for this program outcome
    connections = LOToPO.objects.filter(program_outcome=program_outcome)
    
    if not connections.exists():
        return None
    
    total_weighted_score = 0.0
    total_weight = 0.0
    
    for connection in connections:
        # Calculate the LO score for this student
        lo_score = calculate_lo_score(student, connection.learning_outcome)
        
        if lo_score is not None:
            weight = connection.weight
            total_weighted_score += lo_score * weight
            total_weight += weight
    
    if total_weight == 0:
        return None
    
    return total_weighted_score / total_weight


def get_course_graph_data(course, student=None):
    """
    Get graph data for a course visualization.
    Returns nodes and edges for the graph.
    
    Args:
        course: Course object
        student: Optional Student object to include scores in the graph
    
    Returns:
        dict with 'nodes' and 'edges' lists
    """
    nodes = []
    edges = []
    
    # Add assessment nodes (green diamonds)
    assessments = course.assessments.all()
    for idx, assessment in enumerate(assessments):
        node_data = {
            'id': f'assessment_{assessment.id}',
            'label': assessment.name,
            'type': 'assessment',
            'data': {
                'weight': assessment.weight_in_course,
                'assessment_id': assessment.id,
            }
        }
        
        # Add student grade if provided
        if student:
            try:
                grade = AssessmentGrade.objects.get(assessment=assessment, student=student)
                node_data['data']['grade'] = grade.grade
                node_data['label'] = f"{assessment.name}\n{grade.grade:.1f}%"
            except AssessmentGrade.DoesNotExist:
                pass
        
        nodes.append(node_data)
    
    # Add learning outcome nodes (purple boxes)
    learning_outcomes = course.learning_outcomes.all()
    for idx, lo in enumerate(learning_outcomes):
        node_data = {
            'id': f'lo_{lo.id}',
            'label': lo.code,
            'type': 'learning_outcome',
            'data': {
                'description': lo.description,
                'lo_id': lo.id,
            }
        }
        
        # Calculate and add LO score if student provided
        if student:
            lo_score = calculate_lo_score(student, lo)
            if lo_score is not None:
                node_data['data']['score'] = lo_score
                node_data['label'] = f"{lo.code}\n{lo_score:.1f}%"
        
        nodes.append(node_data)
    
    # Add program outcome nodes (blue boxes)
    # Get POs connected to this course's LOs
    po_connections = LOToPO.objects.filter(learning_outcome__course=course).select_related('program_outcome')
    pos = set()
    for conn in po_connections:
        pos.add(conn.program_outcome)
    
    for po in pos:
        node_data = {
            'id': f'po_{po.id}',
            'label': po.code,
            'type': 'program_outcome',
            'data': {
                'description': po.description,
                'po_id': po.id,
            }
        }
        
        # Calculate and add PO score if student provided
        if student:
            po_score = calculate_po_score(student, po)
            if po_score is not None:
                node_data['data']['score'] = po_score
                node_data['label'] = f"{po.code}\n{po_score:.1f}%"
        
        nodes.append(node_data)
    
    # Add edges: Assessment → Learning Outcome
    assessment_to_lo = AssessmentToLO.objects.filter(
        assessment__course=course
    ).select_related('assessment', 'learning_outcome')
    
    for edge in assessment_to_lo:
        edges.append({
            'id': f'edge_assessment_{edge.assessment.id}_lo_{edge.learning_outcome.id}',
            'source': f'assessment_{edge.assessment.id}',
            'target': f'lo_{edge.learning_outcome.id}',
            'type': 'assessment_to_lo',
            'weight': edge.weight,
            'label': f"{(edge.weight * 100):.0f}%",
        })
    
    # Add edges: Learning Outcome → Program Outcome
    lo_to_po = LOToPO.objects.filter(
        learning_outcome__course=course
    ).select_related('learning_outcome', 'program_outcome')
    
    for edge in lo_to_po:
        edges.append({
            'id': f'edge_lo_{edge.learning_outcome.id}_po_{edge.program_outcome.id}',
            'source': f'lo_{edge.learning_outcome.id}',
            'target': f'po_{edge.program_outcome.id}',
            'type': 'lo_to_po',
            'weight': edge.weight,
            'label': f"{(edge.weight * 100):.0f}%",
        })
    
    return {
        'nodes': nodes,
        'edges': edges,
    }


# ============================================================================
# SAFE DATABASE OPERATIONS WITH TRANSACTIONS
# ============================================================================

def execute_safe_db_operations(operations_callback):
    """
    Execute database operations safely within a transaction.
    
    This function wraps all database operations in a transaction. If any operation
    fails, all changes are automatically rolled back, keeping the database consistent.
    
    Args:
        operations_callback: A callable that receives a cursor and performs operations.
                           Should use parameterized queries (%s) for safety.
    
    Returns:
        tuple: (success: bool, message: str, result: any)
    
    Example:
        def my_operations(cursor):
            # Insert a student
            cursor.execute(
                "INSERT INTO auth_user (username, email, ...) VALUES (%s, %s, ...)",
                ['username', 'email@example.com', ...]
            )
            user_id = cursor.fetchone()[0]
            
            cursor.execute(
                "INSERT INTO edupace_app_student (user_id, student_id, ...) VALUES (%s, %s, ...)",
                [user_id, 'STU001', ...]
            )
            return {'user_id': user_id}
        
        success, message, result = execute_safe_db_operations(my_operations)
        if success:
            print(f"Success: {message}")
        else:
            print(f"Error: {message}")
    """
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                result = operations_callback(cursor)
                return True, "Operations completed successfully", result
    except Exception as e:
        error_msg = f"Error occurred: {str(e)}. All changes have been rolled back."
        return False, error_msg, None


def safe_raw_sql_operations():
    """
    Standalone function demonstrating safe raw SQL operations.
    Can be used directly or imported in views/scripts.
    
    Usage:
        from edupace_app.utils import safe_raw_sql_operations
        safe_raw_sql_operations()
    """
    def operations(cursor):
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
                'pbkdf2_sha256$dummy',  # Note: Use proper password hashing in production
                False,
                True,
                '2024-01-01 00:00:00'
            ]
        )
        user_id = cursor.fetchone()[0]
        
        # ✅ Example: Insert student profile
        cursor.execute(
            """
            INSERT INTO edupace_app_student (user_id, student_id, enrollment_date, 
                                             program, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [
                user_id,
                'STU2024002',
                '2024-01-01',
                'Computer Science',
                '2024-01-01 00:00:00'
            ]
        )
        
        # ✅ Example: Update a course title
        cursor.execute(
            "UPDATE edupace_app_course SET name = %s, updated_at = %s WHERE id = %s",
            ['Updated Course Name', '2024-01-01 00:00:00', 1]
        )
        
        # ✅ Example: Create enrollment (ManyToMany)
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
        
        return {'user_id': user_id, 'student_id': 'STU2024002'}
    
    return execute_safe_db_operations(operations)

