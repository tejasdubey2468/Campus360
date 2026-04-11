
# scheduler/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teachers')
    
    def __str__(self):
        return self.name


class Classroom(models.Model):
    ROOM_TYPES = [
        ('lecture', 'Lecture Hall'),
        ('lab', 'Laboratory'),
        ('seminar', 'Seminar Room'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='lecture')
    capacity = models.PositiveIntegerField(default=30)
    building = models.CharField(max_length=50, blank=True)
    floor = models.CharField(max_length=10, blank=True, help_text="Floor number (e.g., '1st', '2nd', 'Ground')")
    
    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"


class TimeSlot(models.Model):
    DAYS = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),  # Saturday is always a holiday (D-01)
    ]
    
    day = models.IntegerField(choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_lab_slot = models.BooleanField(default=False, help_text="Mark if this is a lab slot (usually 2-3 hours)")
    
    class Meta:
        unique_together = ['day', 'start_time', 'end_time']
        ordering = ['day', 'start_time']
    
    def __str__(self):
        return f"{self.get_day_display()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"


class Class(models.Model):
    """Represents a student class/section like 'CSE 3rd Year Section A'"""
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    section = models.CharField(max_length=10, blank=True)
    strength = models.PositiveIntegerField(default=60)
    
    class Meta:
        verbose_name_plural = "Classes"
    
    def __str__(self):
        return f"{self.name} - Year {self.year} {self.section}"


class Subject(models.Model):
    SUBJECT_TYPES = [
        ('theory', 'Theory'),
        ('lab', 'Laboratory'),
        ('tutorial', 'Tutorial'),
    ]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPES, default='theory')
    credits = models.PositiveIntegerField(default=3)
    hours_per_week = models.PositiveIntegerField(default=3, help_text="Number of lecture hours per week")
    lectures_per_week = models.PositiveIntegerField(default=3, help_text="Number of lectures per week (for scheduling)")
    has_lab_component = models.BooleanField(default=False, help_text="Whether this subject has a lab component")
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class TeacherAvailability(models.Model):
    """Defines when a teacher is available"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='availabilities')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['teacher', 'time_slot']
        verbose_name_plural = "Teacher Availabilities"
    
    def __str__(self):
        status = "Available" if self.is_available else "Unavailable"
        return f"{self.teacher.name} - {self.time_slot} - {status}"


class SubjectAssignment(models.Model):
    """Links subjects to classes and teachers"""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subject_assignments')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='subject_assignments')
    lectures_per_week = models.PositiveIntegerField(default=3, help_text="Number of lectures for this subject in this class per week")
    
    class Meta:
        unique_together = ['subject', 'student_class']
    
    def __str__(self):
        return f"{self.subject.code} - {self.student_class} - {self.teacher.name}"


class Timetable(models.Model):
    """Generated timetable metadata"""
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    
    # Time structure constraints
    start_time = models.TimeField(default='09:00', help_text="Daily start time")
    lecture_duration = models.PositiveIntegerField(default=60, help_text="Lecture duration in minutes")
    lab_duration = models.PositiveIntegerField(default=120, help_text="Lab duration in minutes")
    break_duration = models.PositiveIntegerField(default=30, help_text="Break duration in minutes")
    break_after_slot = models.PositiveIntegerField(default=3, help_text="Break inserted after this slot number")
    
    # Lab constraints
    labs_per_week = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(5)], help_text="Total labs per week (≤ 5)")
    
    # Lecture constraints
    max_consecutive_lectures = models.PositiveIntegerField(default=3, help_text="Maximum consecutive lectures before break")
    allow_same_subject_consecutive = models.BooleanField(default=False, help_text="Allow same subject in consecutive slots")
    
    def __str__(self):
        return f"{self.name} - {self.academic_year} {self.semester}"


class TimetableEntry(models.Model):
    """Individual entries in the timetable"""
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='entries')
    subject_assignment = models.ForeignKey(SubjectAssignment, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['timetable', 'subject_assignment', 'time_slot']
    
    def __str__(self):
        return f"{self.subject_assignment.subject.code} - {self.time_slot} - {self.classroom}"

