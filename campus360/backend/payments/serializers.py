from rest_framework import serializers
from .models import Fee, Payment, PaymentLog


class FeeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.profile.full_name', read_only=True)
    roll_number = serializers.CharField(source='student.roll_number', read_only=True)

    class Meta:
        model = Fee
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.profile.full_name', read_only=True)
    fee_type = serializers.CharField(source='fee.fee_type', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


class PaymentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentLog
        fields = '__all__'


class RazorpayOrderSerializer(serializers.Serializer):
    fee_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class RazorpayVerifySerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()
    fee_id = serializers.UUIDField()
