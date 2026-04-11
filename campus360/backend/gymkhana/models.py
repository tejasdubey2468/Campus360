import uuid
from django.db import models
from students.models import Student
from accounts.models import Profile


class Sport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sports'
        managed = False

    def __str__(self):
        return self.name


class Equipment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    available_quantity = models.IntegerField(default=1)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, blank=True, db_column='sport_id')
    condition = models.CharField(max_length=50, default='GOOD')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equipment'
        managed = False

    def __str__(self):
        return self.equipment_name


class EquipmentBooking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('RETURNED', 'Returned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, db_column='student_id')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, db_column='equipment_id')
    student_name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    booking_date = models.DateField()
    time_slot = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, db_column='approved_by')
    return_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equipment_bookings'
        managed = False


class Turf(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    turf_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, blank=True, db_column='sport_id')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'turfs'
        managed = False

    def __str__(self):
        return self.turf_name


class TurfBooking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, db_column='student_id')
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, db_column='turf_id')
    student_name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    booking_date = models.DateField()
    time_slot = models.CharField(max_length=100)
    contact = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, db_column='approved_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'turf_bookings'
        managed = False
