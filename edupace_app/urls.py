from django.urls import path
from . import views

app_name = 'edupace_app'

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    
    # Student URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/course/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    
    # Teacher URLs
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/course/<int:course_id>/', views.teacher_course_detail, name='teacher_course_detail'),
    path('teacher/course/<int:course_id>/add-learning-outcome/', views.add_learning_outcome, name='add_learning_outcome'),
    path('teacher/learning-outcome/<int:lo_id>/edit/', views.edit_learning_outcome, name='edit_learning_outcome'),
    path('teacher/learning-outcome/<int:lo_id>/delete/', views.delete_learning_outcome, name='delete_learning_outcome'),
    path('teacher/course/<int:course_id>/add-grade/', views.add_grade, name='add_grade'),
    path('teacher/course/<int:course_id>/upload-grades/', views.upload_grades, name='upload_grades'),
    path('teacher/course/<int:course_id>/convert-pdf/', views.convert_grades_to_pdf, name='convert_grades_to_pdf'),
    path('teacher/course/<int:course_id>/add-assessment/', views.add_assessment, name='add_assessment'),
    path('teacher/assessment/<int:assessment_id>/edit/', views.edit_assessment, name='edit_assessment'),
    path('teacher/assessment/<int:assessment_id>/delete/', views.delete_assessment, name='delete_assessment'),
    path('teacher/course/<int:course_id>/add-assessment-grade/', views.add_assessment_grade, name='add_assessment_grade'),
    path('teacher/course/<int:course_id>/connect-assessment-to-lo/', views.connect_assessment_to_lo, name='connect_assessment_to_lo'),
    path('teacher/assessment-to-lo/<int:connection_id>/delete/', views.delete_assessment_to_lo, name='delete_assessment_to_lo'),
    path('teacher/course/<int:course_id>/midterm-outcomes/', views.midterm_outcomes_view, name='midterm_outcomes'),
    
    # Department Head (Academic Board) URLs
    path('academic-board/dashboard/', views.academic_board_dashboard, name='academic_board_dashboard'),
    path('academic-board/student/create/', views.create_student, name='create_student'),
    path('academic-board/teacher/create/', views.create_teacher, name='create_teacher'),
    path('academic-board/course/create/', views.create_course, name='create_course'),
    path('academic-board/course/<int:course_id>/', views.academic_board_course_detail, name='academic_board_course_detail'),
    path('academic-board/course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('academic-board/course/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('academic-board/add-program-outcome/', views.add_program_outcome, name='add_program_outcome'),
    path('academic-board/program-outcome/<int:po_id>/edit/', views.edit_program_outcome, name='edit_program_outcome'),
    path('academic-board/program-outcome/<int:po_id>/delete/', views.delete_program_outcome, name='delete_program_outcome'),
    path('academic-board/course/<int:course_id>/assign-teacher/', views.assign_teacher_to_course, name='assign_teacher_to_course'),
    path('academic-board/course/<int:course_id>/enroll-student/', views.enroll_student_to_course, name='enroll_student_to_course'),
    path('academic-board/course/<int:course_id>/connect-lo-to-po/', views.connect_lo_to_po, name='connect_lo_to_po'),
    path('academic-board/lo-to-po/<int:connection_id>/delete/', views.delete_lo_to_po, name='delete_lo_to_po'),
    
    # API URLs
    path('api/course/<int:course_id>/graph/', views.get_course_graph_api, name='get_course_graph_api'),
]
