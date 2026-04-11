from django.urls import path
from . import views

urlpatterns = [
    path('fees/', views.FeeListView.as_view(), name='fee-list'),
    path('order/create/', views.create_razorpay_order, name='create-order'),
    path('order/verify/', views.verify_payment, name='verify-payment'),
    path('history/', views.PaymentListView.as_view(), name='payment-history'),
]
