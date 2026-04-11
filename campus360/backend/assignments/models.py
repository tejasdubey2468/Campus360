import uuid
from django.db import models
from students.models import Student, Subject
from faculty.models import Faculty


class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_column='subject_id')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, db_column='faculty_id')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file_url = models.TextField(blank=True, null=True)
    max_marks = models.IntegerField(default=100)
    deadline = models.DateTimeField()
    semester = models.IntegerField()
    year = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assignments'
        managed = False

    def __str__(self):
        return self.title


class StudentSubmission(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('GRADED', 'Graded'),
        ('LATE', 'Late'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, db_column='assignment_id')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_id')
    file_url = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    plagiarism_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    graded_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, db_column='graded_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_submissions'
        managed = False


class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_column='subject_id')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, db_column='faculty_id')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file_url = models.TextField(blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    file_size_bytes = models.BigIntegerField(blank=True, null=True)
    semester = models.IntegerField()
    year = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notes'
        managed = False
