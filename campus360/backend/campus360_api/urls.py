from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth & Accounts
    path('api/', include('accounts.urls')),
    # Students
    path('api/student/', include('students.urls')),
    # Faculty
    path('api/faculty/', include('faculty.urls')),
    # Attendance
    path('api/attendance/', include('attendance.urls')),
    # Timetable
    path('api/timetable/', include('timetable.urls')),
    # Assignments
    path('api/assignments/', include('assignments.urls')),
    # Gymkhana (Sports)
    path('api/gymkhana/', include('gymkhana.urls')),
    # Lost & Found
    path('api/lost-found/', include('lost_found.urls')),
    # Payments
    path('api/payments/', include('payments.urls')),
    # Notifications
    path('api/notifications/', include('notifications.urls')),
    # Admin Panel
    path('api/admin-panel/', include('adminpanel.urls')),
    # Classrooms
    path('api/classrooms/', include('classrooms.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
