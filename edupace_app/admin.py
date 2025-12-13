from django.contrib import admin
from .models import (
    Course, Teacher, Student, AcademicBoard,
    ProgramOutcome, LearningOutcome, Grade,
    Assessment, AssessmentGrade, AssessmentToLO, LOToPO
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits', 'is_locked', 'created_at']
    list_filter = ['is_locked', 'created_at']
    search_fields = ['code', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'employee_id']
    filter_horizontal = ['courses']
    readonly_fields = ['created_at']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'program', 'enrollment_date', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'student_id']
    filter_horizontal = ['courses']
    readonly_fields = ['created_at']


@admin.register(AcademicBoard)
class AcademicBoardAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'designation', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'employee_id']
    readonly_fields = ['created_at']


@admin.register(ProgramOutcome)
class ProgramOutcomeAdmin(admin.ModelAdmin):
    list_display = ['code', 'academic_board', 'created_by', 'created_at']
    list_filter = ['academic_board', 'created_at']
    search_fields = ['code', 'description', 'academic_board__user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LearningOutcome)
class LearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ['code', 'course', 'created_by', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['code', 'description', 'course__code', 'course__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'grade', 'percentage', 'semester', 'academic_year', 'created_at']
    list_filter = ['grade', 'course', 'semester', 'academic_year', 'created_at']
    search_fields = ['student__student_id', 'student__user__username', 'course__code', 'course__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'weight_in_course', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['name', 'course__code', 'course__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AssessmentGrade)
class AssessmentGradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'assessment', 'grade', 'created_at']
    list_filter = ['assessment__course', 'created_at']
    search_fields = ['student__student_id', 'student__user__username', 'assessment__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AssessmentToLO)
class AssessmentToLOAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'learning_outcome', 'weight', 'created_at']
    list_filter = ['assessment__course', 'learning_outcome__course', 'created_at']
    search_fields = ['assessment__name', 'learning_outcome__code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LOToPO)
class LOToPOAdmin(admin.ModelAdmin):
    list_display = ['learning_outcome', 'program_outcome', 'weight', 'created_at']
    list_filter = ['learning_outcome__course', 'program_outcome__academic_board', 'created_at']
    search_fields = ['learning_outcome__code', 'program_outcome__code']
    readonly_fields = ['created_at', 'updated_at']
