from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Complaint, JobAllocation, Feedback


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'eis_number', 'role', 'colony_name', 'quarter_no', 'is_staff')
    list_filter = ('role', 'colony_name')
    fieldsets = UserAdmin.fieldsets + (
        ('CCL Details', {'fields': ('eis_number', 'role', 'phone', 'colony_name', 'quarter_no')}),
    )


class JobAllocationInline(admin.StackedInline):
    model = JobAllocation
    extra = 0


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_id', 'resident', 'department', 'issue_type', 
        'priority', 'status', 'created_at', 'check_escalation'
    )
    list_filter = ('department', 'status', 'priority', 'created_at')
    search_fields = ('ticket_id', 'resident__eis_number', 'resident__quarter_no', 'issue_type')
    inlines = [JobAllocationInline]
    readonly_fields = ('ticket_id', 'verification_otp', 'created_at', 'updated_at')

    @admin.display(boolean=True, description='Escalated (>7 Days)')
    def check_escalation(self, obj):
        return obj.is_escalated


@admin.register(JobAllocation)
class JobAllocationAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'assigned_by_je', 'technician_name', 'target_completion_date')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'rating', 'submitted_at')
