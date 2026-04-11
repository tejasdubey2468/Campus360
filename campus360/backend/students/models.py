import uuid
from django.db import models
from accounts.models import Profile, Department


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, db_column='profile_id', related_name='student')
    roll_number = models.CharField(max_length=50, unique=True)
    student_id = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, db_column='department_id')
    year = models.IntegerField()
    semester = models.IntegerField()
    batch = models.CharField(max_length=50, blank=True, null=True)
    admission_date = models.DateField(blank=True, null=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    class_rank = models.IntegerField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    guardian_name = models.CharField(max_length=255, blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)
    guardian_relation = models.CharField(max_length=50, blank=True, null=True)
    fees_status = models.CharField(max_length=20, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        managed = False

    def __str__(self):
        return f"{self.student_id} - {self.profile.full_name}"


class Subject(models.Model):
    SUBJECT_TYPES = [('LECTURE', 'Lecture'), ('LAB', 'Lab'), ('TUTORIAL', 'Tutorial')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, db_column='department_id')
    semester = models.IntegerField()
    credits = models.IntegerField(default=3)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPES, default='LECTURE')
    max_marks = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subjects'
        managed = False

    def __str__(self):
        return f"{self.code} - {self.name}"


class Marks(models.Model):
    GRADE_CHOICES = [
        ('O', 'Outstanding'), ('A+', 'Excellent'), ('A', 'Very Good'),
        ('B+', 'Good'), ('B', 'Above Average'), ('C', 'Average'), ('F', 'Fail'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_id', related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_column='subject_id')
    semester = models.IntegerField()
    internal_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    external_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    max_internal = models.IntegerField(default=40)
    max_external = models.IntegerField(default=60)
    max_total = models.IntegerField(default=100)
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES, blank=True, null=True)
    grade_points = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    credits = models.IntegerField(default=3)
    academic_year = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'marks'
        managed = False


class SemesterResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_id', related_name='semester_results')
    semester = models.IntegerField()
    gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    total_credits = models.IntegerField(default=0)
    earned_credits = models.IntegerField(default=0)
    class_rank = models.IntegerField(blank=True, null=True)
    academic_year = models.CharField(max_length=20, blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'semester_results'
        managed = False
