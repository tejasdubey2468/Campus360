from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/<uuid:profile_id>/', views.profile_view, name='profile-detail'),
    path('profile/<uuid:profile_id>/avatar/', views.upload_avatar, name='upload-avatar'),
    path('departments/', views.DepartmentListView.as_view(), name='department-list'),
]
