import uuid
from django.db import models
from students.models import Student


class Fee(models.Model):
    FEE_TYPES = [
        ('TUITION', 'Tuition Fee'),
        ('EXAM', 'Examination Fee'),
        ('HOSTEL', 'Hostel Fee'),
        ('LIBRARY', 'Library Fee'),
        ('OTHER', 'Other Fee'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_id')
    fee_type = models.CharField(max_length=20, choices=FEE_TYPES)
    description = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    academic_year = models.CharField(max_length=20)
    semester = models.IntegerField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fees'
        managed = False

    def __str__(self):
        return f"{self.fee_type} - {self.student.student_id}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_id')
    fee = models.ForeignKey(Fee, on_delete=models.SET_NULL, null=True, blank=True, db_column='fee_id')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    receipt_url = models.TextField(blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        managed = False


class PaymentLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, db_column='payment_id')
    event = models.CharField(max_length=100)
    details = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_logs'
        managed = False
