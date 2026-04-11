from django import forms

from .models import (
    Department, Teacher, Subject, Classroom, TimeSlot, Class, Timetable, SubjectAssignment
)


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Computer Science'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CS'}),
        }


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'email', 'department']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'subject_type', 'credits', 'hours_per_week', 'lectures_per_week', 'has_lab_component']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CS101'}),
            'subject_type': forms.Select(attrs={'class': 'form-control'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '6'}),
            'hours_per_week': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
            'lectures_per_week': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '7'}),
            'has_lab_component': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name', 'room_type', 'capacity', 'building', 'floor']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room number/name'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '500'}),
            'building': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Building name'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '10'}),
        }


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['day', 'start_time', 'end_time', 'is_lab_slot']
        widgets = {
            'day': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_lab_slot': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'department', 'year', 'section', 'strength']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CS-3A'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
            'section': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A, B, C, etc.'}),
            'strength': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '200'}),
        }


class SubjectAssignmentForm(forms.ModelForm):
    """Form for assigning subjects to classes with lecture counts"""
    class Meta:
        model = SubjectAssignment
        fields = ['subject', 'student_class', 'teacher', 'lectures_per_week']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'student_class': forms.Select(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'lectures_per_week': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '7', 'step': '1'}),
        }


class TimetableGenerateForm(forms.ModelForm):
    """Form for generating timetable with comprehensive constraints"""
    selected_classes = forms.ModelMultipleChoiceField(
        queryset=Class.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        help_text='Select which classes should be included in the timetable generation.'
    )
    
    # Lecture halls and labs for generation
    lecture_classrooms = forms.ModelMultipleChoiceField(
        queryset=Classroom.objects.filter(room_type__in=['lecture', 'seminar']),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        help_text='Select lecture halls and seminar rooms to use.'
    )
    
    lab_classrooms = forms.ModelMultipleChoiceField(
        queryset=Classroom.objects.filter(room_type='lab'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Select lab rooms to use (optional).'
    )

    class Meta:
        model = Timetable
        fields = [
            'name', 'academic_year', 'semester', 
            'start_time', 'lecture_duration', 'lab_duration', 'break_duration', 'break_after_slot',
            'labs_per_week', 'max_consecutive_lectures', 'allow_same_subject_consecutive'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Spring 2024 Timetable'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2024'}),
            'semester': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Spring/Autumn'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'lecture_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '30', 'max': '180', 'step': '15'}),
            'lab_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '60', 'max': '360', 'step': '30'}),
            'break_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '15', 'max': '60', 'step': '5'}),
            'break_after_slot': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10', 'step': '1'}),
            'labs_per_week': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '5', 'step': '1'}),
            'max_consecutive_lectures': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10', 'step': '1'}),
            'allow_same_subject_consecutive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

