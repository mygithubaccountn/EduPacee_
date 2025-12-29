from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import (
    Course, Teacher, Student, AcademicBoard,
    ProgramOutcome, LearningOutcome, Grade,
    Assessment, AssessmentGrade, AssessmentToLO, LOToPO
)


class RoleLoginForm(AuthenticationForm):
    """Login form with role selection"""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('academic_board', 'Department Head'),
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class CourseForm(forms.ModelForm):
    """Form for creating/editing courses (Department Head only)"""
    class Meta:
        model = Course
        fields = ['code', 'name', 'description', 'credits']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }


class ProgramOutcomeForm(forms.ModelForm):
    """Form for creating/editing program outcomes"""
    class Meta:
        model = ProgramOutcome
        fields = ['code', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LearningOutcomeForm(forms.ModelForm):
    """Form for creating/editing learning outcomes"""
    program_outcomes = forms.ModelMultipleChoiceField(
        queryset=ProgramOutcome.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        help_text="Select Program Outcomes to map this Learning Outcome to (optional)"
    )
    
    class Meta:
        model = LearningOutcome
        fields = ['code', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        # If course is provided, we can filter POs if needed in the future
        # For now, show all POs


class GradeUploadForm(forms.Form):
    """Form for uploading Excel file with grades"""
    excel_file = forms.FileField(
        label='Excel File',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        }),
        help_text='Upload an Excel file (.xlsx or .xls) containing student grades'
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Select a course'
    )
    assessment_type = forms.ChoiceField(
        choices=Grade.ASSESSMENT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='final',
        help_text='Select the type of assessment for these grades'
    )
    semester = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Fall 2024'
        })
    )
    academic_year = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 2024-2025'
        })
    )
    
    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['course'].queryset = teacher.courses.all()


class GradeForm(forms.ModelForm):
    """Form for manually entering grades"""
    class Meta:
        model = Grade
        fields = ['student', 'course', 'assessment_type', 'grade', 'percentage', 'semester', 'academic_year']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'assessment_type': forms.Select(attrs={'class': 'form-select'}),
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': 0.01
            }),
            'semester': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['course'].queryset = teacher.courses.all()


class AssignTeacherToCourseForm(forms.Form):
    """Form for assigning teachers to courses"""
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Select a teacher'
    )


class EnrollStudentToCourseForm(forms.Form):
    """Form for enrolling students to courses"""
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Select a student'
    )


class CreateStudentForm(forms.Form):
    """Form for creating a new student"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Password must be at least 8 characters long.'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm Password'
    )
    student_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Unique student ID (e.g., STU001)'
    )
    enrollment_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    program = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Program name (e.g., Computer Science)'
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        return username
    
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if Student.objects.filter(student_id=student_id).exists():
            raise ValidationError('A student with this student ID already exists.')
        return student_id
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError("Passwords don't match.")
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
        
        return cleaned_data


class CreateTeacherForm(forms.Form):
    """Form for creating a new teacher"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Password must be at least 8 characters long.'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm Password'
    )
    employee_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Unique employee ID (e.g., TCH001)'
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Department name (e.g., Computer Science)'
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        return username
    
    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if Teacher.objects.filter(employee_id=employee_id).exists():
            raise ValidationError('A teacher with this employee ID already exists.')
        return employee_id
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError("Passwords don't match.")
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
        
        return cleaned_data


class AssessmentForm(forms.ModelForm):
    """Form for creating/editing assessments"""
    class Meta:
        model = Assessment
        fields = ['name', 'weight_in_course']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'weight_in_course': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'placeholder': '0.0 to 1.0'
            }),
        }


class AssessmentGradeForm(forms.ModelForm):
    """Form for entering assessment grades"""
    class Meta:
        model = AssessmentGrade
        fields = ['assessment', 'student', 'grade']
        widgets = {
            'assessment': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'grade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0.0,
                'max': 100.0,
                'step': 0.1,
                'placeholder': '0-100'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if course:
            self.fields['assessment'].queryset = Assessment.objects.filter(course=course)
            # Use reverse relation to get students enrolled in the course
            self.fields['student'].queryset = course.students.all()


class AssessmentToLOForm(forms.ModelForm):
    """Form for connecting assessments to learning outcomes"""
    class Meta:
        model = AssessmentToLO
        fields = ['assessment', 'learning_outcome', 'weight']
        widgets = {
            'assessment': forms.Select(attrs={'class': 'form-select'}),
            'learning_outcome': forms.Select(attrs={'class': 'form-select'}),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0.0,
                'step': 0.01,
                'placeholder': 'Weight (e.g., 0.6)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if course:
            self.fields['assessment'].queryset = Assessment.objects.filter(course=course)
            self.fields['learning_outcome'].queryset = LearningOutcome.objects.filter(course=course)


class LOToPOForm(forms.ModelForm):
    """Form for connecting learning outcomes to program outcomes"""
    class Meta:
        model = LOToPO
        fields = ['learning_outcome', 'program_outcome', 'weight']
        widgets = {
            'learning_outcome': forms.Select(attrs={'class': 'form-select'}),
            'program_outcome': forms.Select(attrs={'class': 'form-select'}),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0.0,
                'step': 0.01,
                'placeholder': 'Weight (e.g., 1.0)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        academic_board = kwargs.pop('academic_board', None)
        super().__init__(*args, **kwargs)
        if course:
            self.fields['learning_outcome'].queryset = LearningOutcome.objects.filter(course=course)
        if academic_board:
            self.fields['program_outcome'].queryset = ProgramOutcome.objects.filter(academic_board=academic_board)

