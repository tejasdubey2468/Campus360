import uuid
from django.db import models
from faculty.models import Faculty
from accounts.models import Profile


class Classroom(models.Model):
    ROOM_TYPES = [
        ('classroom', 'Classroom'),
        ('lab', 'Laboratory'),
        ('auditorium', 'Auditorium'),
    ]
    OCCUPANCY_STATUS = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='classroom')
    building = models.CharField(max_length=255)
    floor = models.IntegerField(default=0)
    total_seats = models.IntegerField(default=60)
    available_seats = models.IntegerField(default=60)
    status = models.CharField(max_length=20, choices=OCCUPANCY_STATUS, default='available')
    current_faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, db_column='current_faculty_id')
    current_subject = models.CharField(max_length=255, blank=True, null=True)
    current_time_slot = models.CharField(max_length=255, blank=True, null=True)
    equipment = models.JSONField(default=list, blank=True)
    upcoming_info = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'classrooms'
        managed = False

    def __str__(self):
        return f"{self.name} ({self.building})"


class ClassroomBooking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, db_column='classroom_id')
    booked_by = models.ForeignKey(Profile, on_delete=models.CASCADE, db_column='booked_by_id')
    purpose = models.CharField(max_length=255, blank=True, null=True)
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, db_column='approved_by_id', related_name='approved_classrooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'classroom_bookings'
        managed = False
