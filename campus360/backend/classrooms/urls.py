from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.ClassroomListView.as_view(), name='classroom-list'),
    path('<uuid:pk>/', views.ClassroomDetailView.as_view(), name='classroom-detail'),
    path('book/', views.book_classroom, name='book-classroom'),
    path('my-bookings/', views.StudentBookingListView.as_view(), name='my-classroom-bookings'),
]
