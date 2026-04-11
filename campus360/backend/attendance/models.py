import uuid
from django.db import models
from students.models import Student, Subject
from faculty.models import Faculty


class QRSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timetable_slot = models.ForeignKey('timetable.TimetableSlot', on_delete=models.CASCADE, db_column='timetable_slot_id')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, db_column='faculty_id')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_column='subject_id')
    qr_code_data = models.TextField(unique=True)
    qr_image_url = models.TextField(blank=True, null=True)
    session_date = models.DateField()
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'qr_sessions'
        managed = False

    def __str__(self):
        return f"QR Session - {self.subject.name} ({self.session_date})"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_id', related_name='attendance_records')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, db_column='faculty_id')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_column='subject_id')
    timetable_slot = models.ForeignKey('timetable.TimetableSlot', on_delete=models.SET_NULL, null=True, blank=True, db_column='timetable_slot_id')
    qr_session = models.ForeignKey(QRSession, on_delete=models.SET_NULL, null=True, blank=True, db_column='qr_session_id')
    attendance_date = models.DateField()
    attendance_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance'
        managed = False


class AttendanceSummary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_id')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_column='subject_id')
    total_classes = models.IntegerField(default=0)
    present_count = models.IntegerField(default=0)
    absent_count = models.IntegerField(default=0)
    late_count = models.IntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    month = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_summary'
        managed = False
