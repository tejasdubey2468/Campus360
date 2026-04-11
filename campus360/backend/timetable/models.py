import uuid
from django.db import models
from accounts.models import Department
from students.models import Subject
from faculty.models import Faculty


class TimetableSlot(models.Model):
    DAY_CHOICES = [
        ('MONDAY', 'Monday'), ('TUESDAY', 'Tuesday'), ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'), ('FRIDAY', 'Friday'), ('SATURDAY', 'Saturday'),
    ]
    LECTURE_TYPES = [('LECTURE', 'Lecture'), ('LAB', 'Lab'), ('TUTORIAL', 'Tutorial')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, db_column='department_id')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_column='subject_id')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, db_column='faculty_id')
    classroom = models.ForeignKey('classrooms.Classroom', on_delete=models.SET_NULL, null=True, blank=True, db_column='classroom_id')
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    lecture_type = models.CharField(max_length=20, choices=LECTURE_TYPES, default='LECTURE')
    semester = models.IntegerField()
    year = models.IntegerField()
    academic_year = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'timetable_slots'
        managed = False

    def __str__(self):
        return f"{self.day} {self.start_time}-{self.end_time}: {self.subject.name}"
