import razorpay
from django.conf import settings
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Fee, Payment, PaymentLog
from .serializers import FeeSerializer, PaymentSerializer, RazorpayVerifySerializer
from students.models import Student


def get_razorpay_client():
    """Get Razorpay client lazily, only if keys are configured."""
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET
    if not key_id or not key_secret or key_id == 'YOUR_RAZORPAY_KEY_ID':
        return None
    return razorpay.Client(auth=(key_id, key_secret))


class FeeListView(generics.ListCreateAPIView):
    serializer_class = FeeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Fee.objects.select_related('student__profile').all()
        student_id = self.request.query_params.get('student_id')
        is_paid = self.request.query_params.get('is_paid')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if is_paid is not None:
            qs = qs.filter(is_paid=is_paid.lower() == 'true')
        return qs.order_by('due_date')


@api_view(['POST'])
@permission_classes([AllowAny])
def create_razorpay_order(request):
    """Create a Razorpay order relative to a specific fee."""
    client = get_razorpay_client()
    if not client:
        return Response({'error': 'Payment gateway not configured. Please set Razorpay keys.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    fee_id = request.data.get('fee_id')
    try:
        fee = Fee.objects.get(id=fee_id)
        if fee.is_paid:
            return Response({'error': 'Fee is already paid'}, status=status.HTTP_400_BAD_REQUEST)
        
        amount = int(fee.amount * 100)  # Amount in paise
        
        # Create order in Razorpay
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': str(fee.id),
            'payment_capture': 1
        }
        razorpay_order = client.order.create(data=order_data)
        
        # Create a pending payment record
        Payment.objects.create(
            student_id=fee.student_id,
            fee=fee,
            amount=fee.amount,
            razorpay_order_id=razorpay_order['id'],
            status='PENDING'
        )
        
        return Response(razorpay_order)
        
    except Fee.DoesNotExist:
        return Response({'error': 'Fee not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_payment(request):
    """Verify Razorpay payment signature and update fee status."""
    client = get_razorpay_client()
    if not client:
        return Response({'error': 'Payment gateway not configured.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    serializer = RazorpayVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    data = serializer.validated_data
    
    params_dict = {
        'razorpay_order_id': data['razorpay_order_id'],
        'razorpay_payment_id': data['razorpay_payment_id'],
        'razorpay_signature': data['razorpay_signature']
    }
    
    try:
        # Verify signature
        client.utility.verify_payment_signature(params_dict)
        
        # Update Payment record
        payment = Payment.objects.get(razorpay_order_id=data['razorpay_order_id'])
        payment.razorpay_payment_id = data['razorpay_payment_id']
        payment.razorpay_signature = data['razorpay_signature']
        payment.status = 'SUCCESS'
        payment.save()
        
        # Update Fee record
        fee = payment.fee
        fee.is_paid = True
        fee.save()
        
        # Log event
        PaymentLog.objects.create(
            payment=payment,
            event='PAYMENT_VERIFIED',
            details=params_dict
        )
        
        return Response({'message': 'Payment verified successfully'})
        
    except razorpay.errors.SignatureVerificationError:
        # Log failure
        payment = Payment.objects.filter(razorpay_order_id=data['razorpay_order_id']).first()
        if payment:
            payment.status = 'FAILED'
            payment.save()
            
        return Response({'error': 'Invalid payment signature'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Payment.objects.select_related('student__profile', 'fee').all()
        student_id = self.request.query_params.get('student_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs.order_by('-payment_date')
