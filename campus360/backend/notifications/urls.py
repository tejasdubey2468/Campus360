from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-default'),
    path('list/', views.NotificationListView.as_view(), name='notification-list'),
    path('user/', views.UserNotificationListView.as_view(), name='user-notification-list'),
    path('read/<uuid:un_id>/', views.mark_notification_read, name='mark-notification-read'),
]
