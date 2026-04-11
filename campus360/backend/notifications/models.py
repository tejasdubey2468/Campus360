import uuid
from django.db import models
from accounts.models import Profile, Department


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('ANNOUNCEMENT', 'Announcement'),
        ('ALERT', 'Alert'),
        ('ASSIGNMENT', 'Assignment'),
        ('FEE', 'Fee'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, db_column='sender_id')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='ANNOUNCEMENT')
    target_role = models.CharField(max_length=20, blank=True, null=True)
    target_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, db_column='target_department_id')
    target_year = models.IntegerField(blank=True, null=True)
    is_global = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications'
        managed = False

    def __str__(self):
        return self.title


class UserNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, db_column='notification_id')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, db_column='user_id')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_notifications'
        managed = False
