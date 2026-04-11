from django.urls import path
from . import views

urlpatterns = [
    path('system-logs/', views.SystemLogListView.as_view(), name='system-log-list'),
    path('activity-logs/', views.ActivityLogListView.as_view(), name='activity-log-list'),
    path('approvals/', views.AdminApprovalListView.as_view(), name='admin-approval-list'),
    path('analytics/', views.get_admin_analytics, name='admin-analytics'),
]
