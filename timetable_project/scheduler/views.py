# scheduler/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from collections import defaultdict

from .models import (
    Timetable, TimetableEntry, Class, Teacher, Classroom, 
    TimeSlot, Subject, SubjectAssignment, TeacherAvailability,
    Department
)
from .constraints import TimetableGenerator
from .forms import (
    TimetableGenerateForm, DepartmentForm, TeacherForm, SubjectForm,
    ClassroomForm, TimeSlotForm, ClassForm, SubjectAssignmentForm
)


def dashboard(request):
    """Main dashboard view - redirects to data management"""
    return redirect('manage_data')


# ==================== GENERATION DASHBOARD ====================
def generate_timetable_dashboard(request):
    """Dashboard for generating timetable with constraints"""
    if request.method == 'POST':
        form = TimetableGenerateForm(request.POST)
        if form.is_valid():
            selected_classes = form.cleaned_data.get('selected_classes')
            lecture_classrooms = form.cleaned_data.get('lecture_classrooms')
            lab_classrooms = form.cleaned_data.get('lab_classrooms')

            # Create timetable instance with all constraint parameters
            timetable = Timetable.objects.create(
                name=form.cleaned_data['name'],
                academic_year=form.cleaned_data['academic_year'],
                semester=form.cleaned_data['semester'],
                # Time structure constraints
                start_time=form.cleaned_data['start_time'],
                lecture_duration=form.cleaned_data['lecture_duration'],
                lab_duration=form.cleaned_data['lab_duration'],
                break_duration=form.cleaned_data['break_duration'],
                break_after_slot=form.cleaned_data['break_after_slot'],
                # Lab constraints
                labs_per_week=form.cleaned_data['labs_per_week'],
                # Personnel constraints
                max_consecutive_lectures=form.cleaned_data['max_consecutive_lectures'],
                allow_same_subject_consecutive=form.cleaned_data['allow_same_subject_consecutive'],
            )

            # Get subject assignments for selected classes
            selected_assignments = SubjectAssignment.objects.filter(
                student_class__in=selected_classes
            ).select_related('subject', 'student_class', 'teacher')

            # Generate using constraint solver
            generator = TimetableGenerator(
                timetable,
                selected_classes=selected_classes,
                selected_assignments=selected_assignments,
                lecture_classrooms=lecture_classrooms,
                lab_classrooms=lab_classrooms
            )
            result, message = generator.generate()

            if result:
                messages.success(request, message)
                return redirect('view_timetable', pk=timetable.pk)
            else:
                timetable.delete()
                messages.error(request, message)
                # Re-create form with errors
                form = TimetableGenerateForm(request.POST)
    else:
        form = TimetableGenerateForm()

    # Get statistics for the form
    context = {
        'form': form,
        'total_classes': Class.objects.count(),
        'total_subjects': SubjectAssignment.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_time_slots': TimeSlot.objects.count(),
        'lecture_classrooms': Classroom.objects.filter(room_type__in=['lecture', 'seminar']).count(),
        'lab_classrooms': Classroom.objects.filter(room_type='lab').count(),
    }
    return render(request, 'scheduler/generate_timetable_dashboard.html', context)


# ==================== VIEW DASHBOARD ====================
def view_timetable_dashboard(request):
    """Dashboard for viewing all generated timetables"""
    timetables = Timetable.objects.all().order_by('-created_at')
    
    context = {
        'timetables': timetables,
    }
    return render(request, 'scheduler/view_timetables.html', context)


def view_timetable(request, pk):
    """View a specific generated timetable with full schedule"""
    timetable = get_object_or_404(Timetable, pk=pk)
    entries = TimetableEntry.objects.filter(timetable=timetable).select_related(
        'subject_assignment__subject',
        'subject_assignment__teacher',
        'subject_assignment__student_class',
        'time_slot',
        'classroom'
    )
    
    # Use all defined time slots so the timetable grid shows every weekday and every hour
    time_slots = TimeSlot.objects.all().order_by('day', 'start_time')
    classes = Class.objects.all()
    
    # Build a lookup for entries by class and slot
    timetable_grid = defaultdict(dict)
    for entry in entries:
        class_id = entry.subject_assignment.student_class_id
        slot_id = entry.time_slot_id
        timetable_grid[class_id][slot_id] = entry
    
    # Define weekday columns explicitly
    days = [(day, name) for day, name in TimeSlot.DAYS if day < 5]
    
    # Determine unique time rows across all slots
    unique_times = []
    seen_times = set()
    for ts in time_slots:
        key = (ts.start_time, ts.end_time)
        if key not in seen_times:
            seen_times.add(key)
            unique_times.append(key)
    
    # Build a row structure for the table
    rows = []
    for start_time, end_time in unique_times:
        row_slots = []
        for day_num, _ in days:
            slot = next(
                (ts for ts in time_slots if ts.day == day_num and ts.start_time == start_time and ts.end_time == end_time),
                None
            )
            row_slots.append(slot)
        rows.append({
            'start_time': start_time,
            'end_time': end_time,
            'slots': row_slots,
        })
    
    class_schedules = []
    for cls in classes:
        class_id = cls.id
        class_entries = timetable_grid.get(class_id, {})
        class_rows = []
        for row in rows:
            row_cells = []
            for slot in row['slots']:
                row_cells.append(class_entries.get(slot.id) if slot else None)
            class_rows.append({
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'cells': row_cells,
            })
        class_schedules.append({
            'student_class': cls,
            'rows': class_rows,
        })
    
    context = {
        'timetable': timetable,
        'classes': classes,
        'days': days,
        'class_schedules': class_schedules,
        'total_entries': entries.count(),
    }
    return render(request, 'scheduler/timetable_view.html', context)


def view_timetables(request):
    """View all generated timetables"""
    return view_timetable_dashboard(request)


# ==================== DATA MANAGEMENT ====================
def manage_data(request):
    """Combined view for managing all data entities"""
    # Initialize all forms
    department_form = DepartmentForm()
    teacher_form = TeacherForm()
    subject_form = SubjectForm()
    classroom_form = ClassroomForm()
    timeslot_form = TimeSlotForm()
    class_form = ClassForm()
    subject_assignment_form = SubjectAssignmentForm()
    
    # Handle form submissions
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'department':
            department_form = DepartmentForm(request.POST)
            if department_form.is_valid():
                department_form.save()
                messages.success(request, 'Department added successfully.')
                return redirect('manage_data')
        
        elif form_type == 'teacher':
            teacher_form = TeacherForm(request.POST)
            if teacher_form.is_valid():
                teacher_form.save()
                messages.success(request, 'Teacher added successfully.')
                return redirect('manage_data')
        
        elif form_type == 'subject':
            subject_form = SubjectForm(request.POST)
            if subject_form.is_valid():
                subject_form.save()
                messages.success(request, 'Subject added successfully.')
                return redirect('manage_data')
        
        elif form_type == 'classroom':
            classroom_form = ClassroomForm(request.POST)
            if classroom_form.is_valid():
                classroom_form.save()
                messages.success(request, 'Classroom added successfully.')
                return redirect('manage_data')
        
        elif form_type == 'timeslot':
            timeslot_form = TimeSlotForm(request.POST)
            if timeslot_form.is_valid():
                timeslot_form.save()
                messages.success(request, 'Time slot added successfully.')
                return redirect('manage_data')
        
        elif form_type == 'class':
            class_form = ClassForm(request.POST)
            if class_form.is_valid():
                class_form.save()
                messages.success(request, 'Class added successfully.')
                return redirect('manage_data')
        
        elif form_type == 'subject_assignment':
            subject_assignment_form = SubjectAssignmentForm(request.POST)
            if subject_assignment_form.is_valid():
                subject_assignment_form.save()
                messages.success(request, 'Subject assignment added successfully.')
                return redirect('manage_data')
    
    # Get all data for display
    departments = Department.objects.all()
    teachers = Teacher.objects.select_related('department').all()
    subjects = Subject.objects.all()
    classrooms = Classroom.objects.all()
    timeslots = TimeSlot.objects.all().order_by('day', 'start_time')
    classes = Class.objects.select_related('department').all()
    subject_assignments = SubjectAssignment.objects.select_related('subject', 'student_class', 'teacher').all()
    
    context = {
        'department_form': department_form,
        'teacher_form': teacher_form,
        'subject_form': subject_form,
        'classroom_form': classroom_form,
        'timeslot_form': timeslot_form,
        'class_form': class_form,
        'subject_assignment_form': subject_assignment_form,
        'departments': departments,
        'teachers': teachers,
        'subjects': subjects,
        'classrooms': classrooms,
        'timeslots': timeslots,
        'classes': classes,
        'subject_assignments': subject_assignments,
        'total_classes': Class.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_classrooms': Classroom.objects.count(),
    }
    return render(request, 'scheduler/manage_data.html', context)


# ==================== CLASS TIMETABLES ====================
def class_timetable(request, class_id):
    """View timetable for a specific class"""
    student_class = get_object_or_404(Class, pk=class_id)
    active_timetable = Timetable.objects.filter(is_active=True).first()
    
    if not active_timetable:
        messages.warning(request, "No active timetable found.")
        return redirect('dashboard')
    
    entries = TimetableEntry.objects.filter(
        timetable=active_timetable,
        subject_assignment__student_class=student_class
    ).select_related(
        'subject_assignment__subject',
        'subject_assignment__teacher',
        'time_slot',
        'classroom'
    )
    
    # Organize by day and slot
    schedule = defaultdict(dict)
    for entry in entries:
        schedule[entry.time_slot.day][entry.time_slot_id] = entry
    
    # Get time slots used by this class in active timetable
    used_slot_ids = set(e.time_slot_id for e in entries)
    time_slots = TimeSlot.objects.filter(id__in=used_slot_ids).order_by('day', 'start_time')
    unique_times = list(dict.fromkeys((ts.start_time, ts.end_time) for ts in time_slots))
    
    context = {
        'student_class': student_class,
        'schedule': dict(schedule),
        'days': TimeSlot.DAYS,
        'time_slots': time_slots,
        'unique_times': unique_times,
    }
    return render(request, 'scheduler/class_timetable.html', context)


# ==================== TEACHER TIMETABLES ====================
def teacher_timetable(request, teacher_id):
    """View timetable for a specific teacher"""
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    active_timetable = Timetable.objects.filter(is_active=True).first()
    
    if not active_timetable:
        messages.warning(request, "No active timetable found.")
        return redirect('dashboard')
    
    entries = TimetableEntry.objects.filter(
        timetable=active_timetable,
        subject_assignment__teacher=teacher
    ).select_related(
        'subject_assignment__subject',
        'subject_assignment__student_class',
        'time_slot',
        'classroom'
    )
    
    schedule = defaultdict(dict)
    for entry in entries:
        schedule[entry.time_slot.day][entry.time_slot_id] = entry
    
    # Get time slots used by this teacher in active timetable
    used_slot_ids = set(e.time_slot_id for e in entries)
    time_slots = TimeSlot.objects.filter(id__in=used_slot_ids).order_by('day', 'start_time')
    unique_times = list(dict.fromkeys((ts.start_time, ts.end_time) for ts in time_slots))
    
    context = {
        'teacher': teacher,
        'schedule': dict(schedule),
        'days': TimeSlot.DAYS,
        'time_slots': time_slots,
        'unique_times': unique_times,
    }
    return render(request, 'scheduler/teacher_timetable.html', context)


# ==================== TIMETABLE MANAGEMENT ====================
def activate_timetable(request, pk):
    """Activate a timetable"""
    timetable = get_object_or_404(Timetable, pk=pk)
    
    # Deactivate all others
    Timetable.objects.exclude(pk=pk).update(is_active=False)
    
    # Activate this one
    timetable.is_active = True
    timetable.save()
    
    messages.success(request, f'Timetable "{timetable.name}" activated.')
    return redirect('view_timetable_dashboard')


def api_timetable_data(request, pk):
    """API endpoint for timetable data"""
    timetable = get_object_or_404(Timetable, pk=pk)
    entries = TimetableEntry.objects.filter(timetable=timetable).select_related(
        'subject_assignment__subject',
        'subject_assignment__teacher',
        'subject_assignment__student_class',
        'time_slot',
        'classroom'
    )
    
    data = []
    for entry in entries:
        data.append({
            'subject': entry.subject_assignment.subject.name,
            'teacher': entry.subject_assignment.teacher.name,
            'class': entry.subject_assignment.student_class.name,
            'room': entry.classroom.name,
            'day': entry.time_slot.day,
            'start_time': str(entry.time_slot.start_time),
            'end_time': str(entry.time_slot.end_time),
        })
    
    return JsonResponse({'entries': data})


# ==================== CLASS/TEACHER DETAIL VIEWS ====================
def class_detail(request, pk):
    """View class details"""
    student_class = get_object_or_404(Class, pk=pk)
    assignments = SubjectAssignment.objects.filter(
        student_class=student_class
    ).select_related('subject', 'teacher')
    
    context = {
        'class': student_class,
        'assignments': assignments,
    }
    return render(request, 'scheduler/class_detail.html', context)


def teacher_detail(request, pk):
    """View teacher details"""
    teacher = get_object_or_404(Teacher, pk=pk)
    assignments = SubjectAssignment.objects.filter(
        teacher=teacher
    ).select_related('subject', 'student_class')
    
    context = {
        'teacher': teacher,
        'assignments': assignments,
    }
    return render(request, 'scheduler/teacher_detail.html', context)
