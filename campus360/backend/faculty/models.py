import uuid
from django.db import models
from accounts.models import Profile, Department


class Faculty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, db_column='profile_id', related_name='faculty')
    faculty_id = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, db_column='department_id')
    designation = models.CharField(max_length=100, blank=True, null=True)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    specialization = models.CharField(max_length=255, blank=True, null=True)
    join_date = models.DateField(blank=True, null=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    rating = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'faculty'
        managed = False

    def __str__(self):
        return f"{self.faculty_id} - {self.profile.full_name}"


class FacultySubject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, db_column='faculty_id', related_name='assigned_subjects')
    subject = models.ForeignKey('students.Subject', on_delete=models.CASCADE, db_column='subject_id')
    academic_year = models.CharField(max_length=20, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'faculty_subjects'
        managed = False
