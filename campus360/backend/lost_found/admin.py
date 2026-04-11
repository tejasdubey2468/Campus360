from django.contrib import admin
from .models import LostFoundItem, Claim

@admin.register(LostFoundItem)
class LostFoundItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'item_type', 'reporter_name', 'status', 'item_date')
    list_filter = ('item_type', 'status', 'department', 'item_date')
    search_fields = ('item_name', 'description', 'reporter_name', 'roll_number')

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('item', 'claimant_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('claimant_name', 'roll_number', 'details')
    actions = ['approve_claims', 'reject_claims']

    def approve_claims(self, request, queryset):
        for claim in queryset:
            claim.status = 'APPROVED'
            claim.save()
            item = claim.item
            item.status = 'RESOLVED'
            item.save()
    approve_claims.short_description = "Approve selected claims"

    def reject_claims(self, request, queryset):
        queryset.update(status='REJECTED')
    reject_claims.short_description = "Reject selected claims"
