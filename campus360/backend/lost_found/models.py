import uuid
from django.db import models
from accounts.models import Profile


class LostFoundItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('LOST', 'Lost'),
        ('FOUND', 'Found'),
    ]
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    reporter = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, db_column='reporter_id')
    reporter_name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    item_name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    item_date = models.DateField()
    contact = models.CharField(max_length=20, blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    admin_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lost_found_items'
        managed = False

    def __str__(self):
        return f"{self.item_type}: {self.item_name}"


class Claim(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(LostFoundItem, on_delete=models.CASCADE, db_column='item_id', related_name='claims')
    claimant = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, db_column='claimant_id', related_name='my_claims')
    claimant_name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    details = models.TextField()
    proof_image_url = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, db_column='reviewed_by', related_name='reviewed_claims')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'claims'
        managed = False
