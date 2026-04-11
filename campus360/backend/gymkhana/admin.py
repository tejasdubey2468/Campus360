from django.contrib import admin
from .models import Sport, Equipment, EquipmentBooking, Turf, TurfBooking

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('equipment_name', 'category', 'available_quantity', 'quantity')
    search_fields = ('equipment_name', 'category')
    list_filter = ('category',)

@admin.register(EquipmentBooking)
class EquipmentBookingAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'roll_number', 'equipment', 'booking_date', 'time_slot', 'status')
    list_filter = ('status', 'booking_date')
    search_fields = ('student_name', 'roll_number', 'equipment__equipment_name')

@admin.register(Turf)
class TurfAdmin(admin.ModelAdmin):
    list_display = ('turf_name', 'location', 'is_active')
    search_fields = ('turf_name', 'location')
    list_filter = ('is_active',)

@admin.register(TurfBooking)
class TurfBookingAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'roll_number', 'turf', 'booking_date', 'time_slot', 'status')
    list_filter = ('status', 'booking_date')
    search_fields = ('student_name', 'roll_number', 'turf__turf_name')
