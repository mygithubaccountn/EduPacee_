from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse, FileResponse
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.safestring import mark_safe
from django import forms
import os
import tempfile
import json

from .models import (
    Course, Teacher, Student, AcademicBoard,
    ProgramOutcome, LearningOutcome, Grade,
    Assessment, AssessmentGrade, AssessmentToLO, LOToPO
)
from .forms import (
    RoleLoginForm, CourseForm, ProgramOutcomeForm,
    LearningOutcomeForm, GradeUploadForm, GradeForm, AssignTeacherToCourseForm,
    AssessmentForm, AssessmentGradeForm, AssessmentToLOForm, LOToPOForm,
    EnrollStudentToCourseForm
)
from .utils import (
    get_user_role, get_user_profile, role_required,
    check_course_edit_permission, check_learning_outcome_permission,
    check_grade_permission, excel_to_pdf, process_excel_grades,
    get_course_graph_data, calculate_lo_score, calculate_po_score
)


def login_view(request):
    """Login view with role selection"""
    if request.user.is_authenticated:
        return redirect('edupace_app:dashboard_redirect')
    
    if request.method == 'POST':
        form = RoleLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            role = form.cleaned_data.get('role')
            
            # Verify user has the selected role
            user_role = get_user_role(user)
            if user_role != role:
                messages.error(request, f'This account is not registered as a {role.title()}.')
                return render(request, 'edupace_app/login.html', {'form': form})
            
            login(request, user)
            messages.success(request, f'Welcome, {user.get_full_name() or user.username}!')
            return redirect('edupace_app:dashboard_redirect')
    else:
        form = RoleLoginForm()
    
    return render(request, 'edupace_app/login.html', {'form': form})


@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('edupace_app:login')


@login_required
def dashboard_redirect(request):
    """Redirect user to their role-specific dashboard"""
    role = get_user_role(request.user)
    
    if role == 'student':
        return redirect('edupace_app:student_dashboard')
    elif role == 'teacher':
        return redirect('edupace_app:teacher_dashboard')
    elif role == 'academic_board':
        return redirect('edupace_app:academic_board_dashboard')
    else:
        messages.error(request, 'Your account is not associated with any role.')
        return redirect('edupace_app:login')


# ==================== STUDENT VIEWS ====================

@login_required
@role_required('student')
def student_dashboard(request):
    """Student dashboard - view grades, program outcomes, learning outcomes"""
    student = get_user_profile(request.user)
    courses = student.courses.all()
    grades = Grade.objects.filter(student=student).select_related('course')
    
    context = {
        'student': student,
        'courses': courses,
        'grades': grades,
    }
    return render(request, 'edupace_app/student/dashboard.html', context)


@login_required
@role_required('student')
def student_course_detail(request, course_id):
    """Student view of a specific course"""
    student = get_user_profile(request.user)
    course = get_object_or_404(Course, id=course_id)
    
    # Check if student is enrolled
    if course not in student.courses.all():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('edupace_app:student_dashboard')
    
    grade = Grade.objects.filter(student=student, course=course).first()
    
    # Get graph data with student scores
    graph_data = get_course_graph_data(course, student=student)
    graph_data_json = mark_safe(json.dumps(graph_data))
    
    # Calculate LO and PO scores for display
    learning_outcomes = course.learning_outcomes.all()
    lo_scores = {}
    lo_scores_list = []
    for lo in learning_outcomes:
        score = calculate_lo_score(student, lo)
        if score is not None:
            lo_scores[lo.id] = score
            lo_scores_list.append({'lo': lo, 'score': score})
    
    # Get POs connected to this course's LOs
    po_connections = LOToPO.objects.filter(learning_outcome__course=course).select_related('program_outcome')
    pos = {}
    for conn in po_connections:
        if conn.program_outcome.id not in pos:
            pos[conn.program_outcome.id] = conn.program_outcome
    
    po_scores = {}
    po_scores_list = []
    for po_id, po in pos.items():
        score = calculate_po_score(student, po)
        if score is not None:
            po_scores[po_id] = score
            po_scores_list.append({'po': po, 'score': score})
    
    context = {
        'course': course,
        'grade': grade,
        'learning_outcomes': learning_outcomes,
        'program_outcomes': pos.values(),
        'lo_scores': lo_scores,
        'po_scores': po_scores,
        'lo_scores_list': lo_scores_list,
        'po_scores_list': po_scores_list,
        'graph_data': graph_data_json,
    }
    return render(request, 'edupace_app/student/course_detail.html', context)


# ==================== TEACHER VIEWS ====================

@login_required
@role_required('teacher')
def teacher_dashboard(request):
    """Teacher dashboard"""
    teacher = get_user_profile(request.user)
    courses = teacher.courses.all()
    
    # Get statistics
    total_courses = courses.count()
    courses_with_los = courses.filter(learning_outcomes__isnull=False).distinct().count()
    
    context = {
        'teacher': teacher,
        'courses': courses,
        'total_courses': total_courses,
        'courses_with_los': courses_with_los,
    }
    return render(request, 'edupace_app/teacher/dashboard.html', context)


@login_required
@role_required('teacher')
def teacher_course_detail(request, course_id):
    """Teacher view of a specific course"""
    teacher = get_user_profile(request.user)
    course = get_object_or_404(Course, id=course_id)
    
    # Check if teacher teaches this course
    if course not in teacher.courses.all():
        messages.error(request, 'You do not teach this course.')
        return redirect('edupace_app:teacher_dashboard')
    
    learning_outcomes = course.learning_outcomes.all()
    assessments = course.assessments.all()
    assessment_to_lo = AssessmentToLO.objects.filter(assessment__course=course).select_related('assessment', 'learning_outcome')
    grades = Grade.objects.filter(course=course).select_related('student')
    
    # Get graph data
    graph_data = get_course_graph_data(course)
    graph_data_json = mark_safe(json.dumps(graph_data))
    
    context = {
        'course': course,
        'learning_outcomes': learning_outcomes,
        'assessments': assessments,
        'assessment_to_lo': assessment_to_lo,
        'grades': grades,
        'graph_data': graph_data_json,
    }
    return render(request, 'edupace_app/teacher/course_detail.html', context)


@login_required
@role_required('teacher')
def add_learning_outcome(request, course_id):
    """Add learning outcome to a course"""
    teacher = get_user_profile(request.user)
    course = get_object_or_404(Course, id=course_id)
    
    # Check permissions
    if not check_learning_outcome_permission(request.user, course):
        messages.error(request, 'You cannot add learning outcomes to this course.')
        return redirect('edupace_app:teacher_course_detail', course_id=course_id)
    
    if request.method == 'POST':
        form = LearningOutcomeForm(request.POST)
        if form.is_valid():
            learning_outcome = form.save(commit=False)
            learning_outcome.course = course
            learning_outcome.created_by = request.user
            learning_outcome.save()
            messages.success(request, f'Learning outcome {learning_outcome.code} added successfully.')
            return redirect('edupace_app:teacher_course_detail', course_id=course_id)
    else:
        form = LearningOutcomeForm()
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'edupace_app/teacher/add_learning_outcome.html', context)


@login_required
@role_required('teacher')
def edit_learning_outcome(request, lo_id):
    """Edit a learning outcome"""
    learning_outcome = get_object_or_404(LearningOutcome, id=lo_id)
    teacher = get_user_profile(request.user)
    
    # Check permissions
    if learning_outcome.course not in teacher.courses.all():
        messages.error(request, 'You do not have permission to edit this learning outcome.')
        return redirect('edupace_app:teacher_dashboard')
    
    if request.method == 'POST':
        form = LearningOutcomeForm(request.POST, instance=learning_outcome)
        if form.is_valid():
            form.save()
            messages.success(request, 'Learning outcome updated successfully.')
            return redirect('edupace_app:teacher_course_detail', course_id=learning_outcome.course.id)
    else:
        form = LearningOutcomeForm(instance=learning_outcome)
    
    context = {
        'form': form,
        'learning_outcome': learning_outcome,
        'course': learning_outcome.course,
    }
    return render(request, 'edupace_app/teacher/edit_learning_outcome.html', context)


@login_required
@role_required('teacher')
def delete_learning_outcome(request, lo_id):
    """Delete a learning outcome"""
    learning_outcome = get_object_or_404(LearningOutcome, id=lo_id)
    teacher = get_user_profile(request.user)
    course = learning_outcome.course
    
    # Check permissions
    if course not in teacher.courses.all():
        messages.error(request, 'You do not have permission to delete this learning outcome.')
        return redirect('edupace_app:teacher_dashboard')
    
    if request.method == 'POST':
        learning_outcome.delete()
        messages.success(request, 'Learning outcome deleted successfully.')
        return redirect('edupace_app:teacher_course_detail', course_id=course.id)
    
    context = {
        'learning_outcome': learning_outcome,
        'course': course,
    }
    return render(request, 'edupace_app/teacher/delete_learning_outcome.html', context)


@login_required
@role_required('teacher')
def add_grade(request, course_id):
    """Add a single grade manually for a student"""
    teacher = get_user_profile(request.user)
    course = get_object_or_404(Course, id=course_id)
    
    # Check permissions
    if not check_grade_permission(request.user, course):
        messages.error(request, 'You cannot add grades for this course.')
        return redirect('edupace_app:teacher_course_detail', course_id=course_id)
    
    if request.method == 'POST':
        form = GradeForm(request.POST, teacher=teacher)
        if form.is_valid():
            # Ensure the course matches
            if form.cleaned_data['course'] != course:
                messages.error(request, 'Course mismatch.')
                return redirect('edupace_app:teacher_course_detail', course_id=course_id)
            
            grade, created = Grade.objects.update_or_create(
                student=form.cleaned_data['student'],
                course=course,
                semester=form.cleaned_data.get('semester', ''),
                academic_year=form.cleaned_data.get('academic_year', ''),
                defaults={
                    'grade': form.cleaned_data['grade'],
                    'percentage': form.cleaned_data.get('percentage'),
                    'created_by': request.user,
                }
            )
            if created:
                messages.success(request, f'Grade added successfully for {grade.student.user.get_full_name() or grade.student.student_id}.')
            else:
                messages.success(request, f'Grade updated successfully for {grade.student.user.get_full_name() or grade.student.student_id}.')
            return redirect('edupace_app:teacher_course_detail', course_id=course_id)
    else:
        form = GradeForm(teacher=teacher, initial={'course': course})
        # Filter students to only those enrolled in this course (use reverse relation)
        form.fields['student'].queryset = course.students.all()
        # Hide course field since it's already set
        form.fields['course'].widget = forms.HiddenInput()
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'edupace_app/teacher/add_grade.html', context)


@login_required
@role_required('teacher')
def upload_grades(request, course_id):
    """Upload grades via Excel file"""
    teacher = get_user_profile(request.user)
    course = get_object_or_404(Course, id=course_id)
    
    # Check permissions
    if not check_grade_permission(request.user, course):
        messages.error(request, 'You cannot upload grades for this course.')
        return redirect('edupace_app:teacher_course_detail', course_id=course_id)
    
    if request.method == 'POST':
        form = GradeUploadForm(request.POST, request.FILES, teacher=teacher)
        if form.is_valid():
            excel_file = form.cleaned_data['excel_file']
            semester = form.cleaned_data.get('semester', '')
            academic_year = form.cleaned_data.get('academic_year', '')
            
            # Process Excel file
            success, message, errors = process_excel_grades(
                excel_file, course, semester, academic_year, request.user
            )
            
            if success:
                messages.success(request, message)
                if errors:
                    for error in errors[:10]:  # Show first 10 errors
                        messages.warning(request, error)
            else:
                messages.error(request, message)
            
            return redirect('edupace_app:teacher_course_detail', course_id=course_id)
    else:
        form = GradeUploadForm(teacher=teacher, initial={'course': course})
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'edupace_app/teacher/upload_grades.html', context)


@login_required
@role_required('teacher')
def convert_grades_to_pdf(request, course_id):
    """Convert grades Excel to PDF"""
    teacher = get_user_profile(request.user)
    course = get_object_or_404(Course, id=course_id)
    
    if course not in teacher.courses.all():
        messages.error(request, 'You do not teach this course.')
        return redirect('edupace_app:teacher_dashboard')
    
    grades = Grade.objects.filter(course=course).select_related('student')
    
    if not grades.exists():
        messages.error(request, 'No grades found for this course.')
        return redirect('edupace_app:teacher_course_detail', course_id=course_id)
    
    # Create temporary Excel file
    try:
        import pandas as pd
        
        data = []
        for grade in grades:
            data.append({
                'Student ID': grade.student.student_id,
                'Student Name': grade.student.user.get_full_name() or grade.student.user.username,
                'Grade': grade.grade,
                'Percentage': grade.percentage or '',
                'Semester': grade.semester or '',
                'Academic Year': grade.academic_year or '',
            })
        
        df = pd.DataFrame(data)
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_excel:
            df.to_excel(tmp_excel.name, index=False)
            excel_path = tmp_excel.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            pdf_path = tmp_pdf.name
        
        # Convert to PDF
        if excel_to_pdf(excel_path, pdf_path):
            response = FileResponse(
                open(pdf_path, 'rb'),
                content_type='application/pdf',
                filename=f'{course.code}_grades.pdf'
            )
            # Clean up
            os.unlink(excel_path)
            return response
        else:
            messages.error(request, 'Error converting grades to PDF.')
            os.unlink(excel_path)
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            return redirect('edupace_app:teacher_course_detail', course_id=course_id)
            
    except Exception as e:
        messages.error(request, f'Error generating PDF: {str(e)}')
        return redirect('edupace_app:teacher_course_detail', course_id=course_id)


# ==================== ACADEMIC BOARD VIEWS ====================

@login_required
@role_required('academic_board')
def academic_board_dashboard(request):
    """Academic Board dashboard"""
    courses = Course.objects.all()
    total_courses = courses.count()
    
    context = {
        'courses': courses,
        'total_courses': total_courses,
    }
    return render(request, 'edupace_app/academic_board/dashboard.html', context)


@login_required
@role_required('academic_board')
def create_course(request):
    """Create a new course"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course {course.code} created successfully.')
            return redirect('edupace_app:academic_board_course_detail', course_id=course.id)
    else:
        form = CourseForm()
    
    return render(request, 'edupace_app/academic_board/create_course.html', {'form': form})


@login_required
@role_required('academic_board')
def academic_board_course_detail(request, course_id):
    """Academic Board view of a specific course"""
    course = get_object_or_404(Course, id=course_id)
    academic_board = get_user_profile(request.user)
    
    # Get POs for this academic board
    program_outcomes = ProgramOutcome.objects.filter(academic_board=academic_board)
    learning_outcomes = course.learning_outcomes.all()
    lo_to_po = LOToPO.objects.filter(learning_outcome__course=course).select_related('learning_outcome', 'program_outcome')
    teachers = course.teachers.all()
    students = course.students.all()
    grades = Grade.objects.filter(course=course).select_related('student')
    
    # Get graph data
    graph_data = get_course_graph_data(course)
    graph_data_json = mark_safe(json.dumps(graph_data))
    
    context = {
        'course': course,
        'program_outcomes': program_outcomes,
        'learning_outcomes': learning_outcomes,
        'lo_to_po': lo_to_po,
        'teachers': teachers,
        'students': students,
        'grades': grades,
        'graph_data': graph_data_json,
    }
    return render(request, 'edupace_app/academic_board/course_detail.html', context)


@login_required
@role_required('academic_board')
def edit_course(request, course_id):
    """Edit a course"""
    course = get_object_or_404(Course, id=course_id)
    
    # Check if course can be edited
    if not check_course_edit_permission(request.user, course):
        messages.error(request, 'This course is locked and cannot be edited.')
        return redirect('edupace_app:academic_board_course_detail', course_id=course_id)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('edupace_app:academic_board_course_detail', course_id=course_id)
    else:
        form = CourseForm(instance=course)
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'edupace_app/academic_board/edit_course.html', context)


@login_required
@role_required('academic_board')
def delete_course(request, course_id):
    """Delete a course"""
    course = get_object_or_404(Course, id=course_id)
    
    if not check_course_edit_permission(request.user, course):
        messages.error(request, 'This course is locked and cannot be deleted.')
        return redirect('edupace_app:academic_board_course_detail', course_id=course_id)
    
    if request.method == 'POST':
        course_code = course.code
        course.delete()
        messages.success(request, f'Course {course_code} deleted successfully.')
        return redirect('edupace_app:academic_board_dashboard')
    
    return render(request, 'edupace_app/academic_board/delete_course.html', {'course': course})


@login_required
@role_required('academic_board')
def add_program_outcome(request):
    """Add program outcome (Academic Board level, not course-specific)"""
    academic_board = get_user_profile(request.user)
    
    if request.method == 'POST':
        form = ProgramOutcomeForm(request.POST)
        if form.is_valid():
            try:
                program_outcome = form.save(commit=False)
                program_outcome.academic_board = academic_board
                program_outcome.created_by = request.user
                program_outcome.save()
                messages.success(request, f'Program outcome {program_outcome.code} added successfully.')
                return redirect('edupace_app:academic_board_dashboard')
            except Exception as e:
                messages.error(request, f'Error saving program outcome: {str(e)}')
        # If form is invalid, fall through to render form with errors
    else:
        form = ProgramOutcomeForm()
    
    context = {
        'form': form,
    }
    return render(request, 'edupace_app/academic_board/add_program_outcome.html', context)


@login_required
@role_required('academic_board')
def edit_program_outcome(request, po_id):
    """Edit a program outcome"""
    program_outcome = get_object_or_404(ProgramOutcome, id=po_id)
    academic_board = get_user_profile(request.user)
    
    # Check if PO belongs to this academic board
    if program_outcome.academic_board != academic_board:
        messages.error(request, 'You do not have permission to edit this program outcome.')
        return redirect('edupace_app:academic_board_dashboard')
    
    if request.method == 'POST':
        form = ProgramOutcomeForm(request.POST, instance=program_outcome)
        if form.is_valid():
            form.save()
            messages.success(request, 'Program outcome updated successfully.')
            return redirect('edupace_app:academic_board_dashboard')
    else:
        form = ProgramOutcomeForm(instance=program_outcome)
    
    context = {
        'form': form,
        'program_outcome': program_outcome,
    }
    return render(request, 'edupace_app/academic_board/edit_program_outcome.html', context)


@login_required
@role_required('academic_board')
def delete_program_outcome(request, po_id):
    """Delete a program outcome"""
    program_outcome = get_object_or_404(ProgramOutcome, id=po_id)
    academic_board = get_user_profile(request.user)
    
    # Check if PO belongs to this academic board
    if program_outcome.academic_board != academic_board:
        messages.error(request, 'You do not have permission to delete this program outcome.')
        return redirect('edupace_app:academic_board_dashboard')
    
    if request.method == 'POST':
        program_outcome.delete()
        messages.success(request, 'Program outcome deleted successfully.')
        return redirect('edupace_app:academic_board_dashboard')
    
    context = {
        'program_outcome': program_outcome,
    }
    return render(request, 'edupace_app/academic_board/delete_program_outcome.html', context)


@login_required
@role_required('academic_board')
def assign_teacher_to_course(request, course_id):
    """Assign a teacher to a course"""
    course = get_object_or_404(Course, id=course_id)
    
    if not check_course_edit_permission(request.user, course):
        messages.error(request, 'This course is locked. You cannot assign teachers.')
        return redirect('edupace_app:academic_board_course_detail', course_id=course_id)
    
    if request.method == 'POST':
        form = AssignTeacherToCourseForm(request.POST)
        if form.is_valid():
            teacher = form.cleaned_data['teacher']
            course.teachers.add(teacher)
            messages.success(request, f'Teacher {teacher.user.get_full_name()} assigned to course.')
            return redirect('edupace_app:academic_board_course_detail', course_id=course_id)
    else:
        form = AssignTeacherToCourseForm()
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'edupace_app/academic_board/assign_teacher.html', context)


@login_required
@role_required('academic_board')
def enroll_student_to_course(request, course_id):
    """Enroll a student to a course"""
    course = get_object_or_404(Course, id=course_id)
    
    if not check_course_edit_permission(request.user, course):
        messages.error(request, 'This course is locked. You cannot enroll students.')
        return redirect('edupace_app:academic_board_course_detail', course_id=course_id)
    
    # Get students not already enrolled in this course
    enrolled_student_ids = course.students.values_list('id', flat=True)
    available_students = Student.objects.exclude(id__in=enrolled_student_ids)
    
    if request.method == 'POST':
        form = EnrollStudentToCourseForm(request.POST)
        # Set queryset to only available students
        form.fields['student'].queryset = available_students
        if form.is_valid():
            student = form.cleaned_data['student']
            # Double-check student is not already enrolled
            if student in course.students.all():
                messages.warning(request, f'Student {student.user.get_full_name()} is already enrolled in this course.')
            else:
                course.students.add(student)
                messages.success(request, f'Student {student.user.get_full_name()} enrolled in course.')
            return redirect('edupace_app:academic_board_course_detail', course_id=course_id)
    else:
        form = EnrollStudentToCourseForm()
        # Filter out students already enrolled in this course
        form.fields['student'].queryset = available_students
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'edupace_app/academic_board/enroll_student.html', context)


# ==================== ASSESSMENT MANAGEMENT (TEACHER) ====================

@login_required
@role_required('teacher')
def add_assessment(request, course_id):
    """Add assessment to a course"""
    teacher = get_user_profile(request.user)
    course = get_object_or_404(Course, id=course_id)
    
    if course not in teacher.courses.all():
        messages.error(request, 'You do not teach this course.')
        return redirect('edupace_app:teacher_dashboard')
    
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.course = course
            assessment.save()
            messages.success(request, f'Assessment {assessment.name} added successfully.')
            return redirect('edupace_app:teacher_course_detail', course_id=course_id)
    else:
        form = AssessmentForm()
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'edupace_app/teacher/add_assessment.html', context)


@login_required
@role_required('teacher')
def edit_assessment(request, assessment_id):
    """Edit an assessment"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    teacher = get_user_profile(request.user)
    
    if assessment.course not in teacher.courses.all():
        messages.error(request, 'You do not have permission to edit this assessment.')
        return redirect('edupace_app:teacher_dashboard')
    
    if request.method == 'POST':
        form = AssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assessment updated successfully.')
            return redirect('edupace_app:teacher_course_detail', course_id=assessment.course.id)
    else:
        form = AssessmentForm(instance=assessment)
    
    context = {
        'form': form,
        'assessment': assessment,
        'course': assessment.course,
    }
    return render(request, 'edupace_app/teacher/edit_assessment.html', context)


@login_required
@role_required('teacher')
def delete_assessment(request, assessment_id):
    """Delete an assessment"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    teacher = get_user_profile(request.user)
    course = assessment.course
    
    if course not in teacher.courses.all():
        messages.error(request, 'You do not have permission to delete this assessment.')
        return redirect('edupace_app:teacher_dashboard')
    
    if request.method == 'POST':
        assessment.delete()
        messages.success(request, 'Assessment deleted successfully.')
        return redirect('edupace_app:teacher_course_detail', course_id=course.id)
    
    context = {
        'assessment': assessment,
        'course': course,
    }
    return render(request, 'edupace_app/teacher/delete_assessment.html', context)


@login_required
@role_required('teacher')
def add_assessment_grade(request, course_id):
    """Add assessment grade for a student"""
    teacher = get_user_profile(request.user)
    course = get_object_or_404(Course, id=course_id)
    
    if course not in teacher.courses.all():
        messages.error(request, 'You do not teach this course.')
        return redirect('edupace_app:teacher_dashboard')
    
    if request.method == 'POST':
        form = AssessmentGradeForm(request.POST, course=course)
        if form.is_valid():
            grade, created = AssessmentGrade.objects.update_or_create(
                assessment=form.cleaned_data['assessment'],
                student=form.cleaned_data['student'],
                defaults={'grade': form.cleaned_data['grade']}
            )
            if created:
                messages.success(request, 'Assessment grade added successfully.')
            else:
                messages.success(request, 'Assessment grade updated successfully.')
            return redirect('edupace_app:teacher_course_detail', course_id=course_id)
    else:
        form = AssessmentGradeForm(course=course)
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'edupace_app/teacher/add_assessment_grade.html', context)


@login_required
@role_required('teacher')
def connect_assessment_to_lo(request, course_id):
    """Connect assessment to learning outcome with weight"""
    teacher = get_user_profile(request.user)
    course = get_object_or_404(Course, id=course_id)
    
    if course not in teacher.courses.all():
        messages.error(request, 'You do not teach this course.')
        return redirect('edupace_app:teacher_dashboard')
    
    if request.method == 'POST':
        form = AssessmentToLOForm(request.POST, course=course)
        if form.is_valid():
            connection, created = AssessmentToLO.objects.update_or_create(
                assessment=form.cleaned_data['assessment'],
                learning_outcome=form.cleaned_data['learning_outcome'],
                defaults={'weight': form.cleaned_data['weight']}
            )
            if created:
                messages.success(request, 'Connection created successfully.')
            else:
                messages.success(request, 'Connection updated successfully.')
            return redirect('edupace_app:teacher_course_detail', course_id=course_id)
    else:
        form = AssessmentToLOForm(course=course)
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'edupace_app/teacher/connect_assessment_to_lo.html', context)


@login_required
@role_required('teacher')
def delete_assessment_to_lo(request, connection_id):
    """Delete assessment to LO connection"""
    connection = get_object_or_404(AssessmentToLO, id=connection_id)
    teacher = get_user_profile(request.user)
    course = connection.assessment.course
    
    if course not in teacher.courses.all():
        messages.error(request, 'You do not have permission to delete this connection.')
        return redirect('edupace_app:teacher_dashboard')
    
    if request.method == 'POST':
        connection.delete()
        messages.success(request, 'Connection deleted successfully.')
        return redirect('edupace_app:teacher_course_detail', course_id=course.id)
    
    context = {
        'connection': connection,
        'course': course,
    }
    return render(request, 'edupace_app/teacher/delete_assessment_to_lo.html', context)


# ==================== LO TO PO CONNECTIONS (ACADEMIC BOARD) ====================

@login_required
@role_required('academic_board')
def connect_lo_to_po(request, course_id):
    """Connect learning outcome to program outcome with weight"""
    course = get_object_or_404(Course, id=course_id)
    academic_board = get_user_profile(request.user)
    
    if request.method == 'POST':
        form = LOToPOForm(request.POST, course=course, academic_board=academic_board)
        if form.is_valid():
            connection, created = LOToPO.objects.update_or_create(
                learning_outcome=form.cleaned_data['learning_outcome'],
                program_outcome=form.cleaned_data['program_outcome'],
                defaults={'weight': form.cleaned_data['weight']}
            )
            if created:
                messages.success(request, 'Connection created successfully.')
            else:
                messages.success(request, 'Connection updated successfully.')
            return redirect('edupace_app:academic_board_course_detail', course_id=course_id)
    else:
        form = LOToPOForm(course=course, academic_board=academic_board)
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'edupace_app/academic_board/connect_lo_to_po.html', context)


@login_required
@role_required('academic_board')
def delete_lo_to_po(request, connection_id):
    """Delete LO to PO connection"""
    connection = get_object_or_404(LOToPO, id=connection_id)
    course = connection.learning_outcome.course
    
    if request.method == 'POST':
        connection.delete()
        messages.success(request, 'Connection deleted successfully.')
        return redirect('edupace_app:academic_board_course_detail', course_id=course.id)
    
    context = {
        'connection': connection,
        'course': course,
    }
    return render(request, 'edupace_app/academic_board/delete_lo_to_po.html', context)


# ==================== API ENDPOINTS ====================

@login_required
def get_course_graph_api(request, course_id):
    """API endpoint to get graph data for a course"""
    course = get_object_or_404(Course, id=course_id)
    student = None
    
    # If student, get their profile
    if get_user_role(request.user) == 'student':
        student = get_user_profile(request.user)
        if course not in student.courses.all():
            return JsonResponse({'error': 'Not enrolled in this course'}, status=403)
    
    graph_data = get_course_graph_data(course, student=student)
    return JsonResponse(graph_data)
