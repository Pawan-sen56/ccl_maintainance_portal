from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from .models import CustomUser, Complaint, JobAllocation, Feedback
from .forms import (
    CustomUserRegistrationForm, 
    ComplaintForm, 
    JobAllocationForm, 
    OTPVerificationForm, 
    FeedbackForm
)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to CCL Township Portal, {user.first_name or user.username}!")
            return redirect('dashboard')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'maintenance/register.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}

    if user.role == 'RESIDENT':
        complaints = Complaint.objects.filter(resident=user).order_by('-created_at')
        context['complaints'] = complaints
        context['total_count'] = complaints.count()
        context['pending_count'] = complaints.exclude(status='CLOSED').count()
        context['closed_count'] = complaints.filter(status='CLOSED').count()
        return render(request, 'maintenance/resident_dashboard.html', context)

    elif user.role in ['JE_CIVIL', 'JE_ELEC']:
        dept = 'CIVIL' if user.role == 'JE_CIVIL' else 'ELECTRICAL'
        # Can see both Civil and Water Supply if JE_CIVIL
        dept_filter = Q(department=dept) | Q(department='WATER_SUPPLY') if user.role == 'JE_CIVIL' else Q(department=dept)
        
        complaints = Complaint.objects.filter(dept_filter).order_by('-created_at')
        context['complaints'] = complaints
        context['dept_name'] = "Civil & Public Health" if user.role == 'JE_CIVIL' else "Electrical"
        context['total_count'] = complaints.count()
        context['unassigned_count'] = complaints.filter(status='SUBMITTED').count()
        context['active_count'] = complaints.filter(status__in=['ASSIGNED', 'IN_PROGRESS']).count()
        context['escalated_count'] = sum(1 for c in complaints if c.is_escalated)
        return render(request, 'maintenance/je_dashboard.html', context)

    elif user.role == 'STAFF_OFFICER' or user.is_staff or user.is_superuser:
        all_complaints = Complaint.objects.all().order_by('-created_at')
        context['complaints'] = all_complaints
        context['total_count'] = all_complaints.count()
        context['pending_count'] = all_complaints.exclude(status='CLOSED').count()
        context['closed_count'] = all_complaints.filter(status='CLOSED').count()
        
        # Calculate escalated tickets (> 7 days unresolved)
        escalated_list = [c for c in all_complaints if c.is_escalated]
        context['escalated_complaints'] = escalated_list
        context['escalated_count'] = len(escalated_list)

        # Department breakdown
        context['civil_count'] = all_complaints.filter(department='CIVIL').count()
        context['elec_count'] = all_complaints.filter(department='ELECTRICAL').count()
        context['water_count'] = all_complaints.filter(department='WATER_SUPPLY').count()

        return render(request, 'maintenance/officer_dashboard.html', context)

    return render(request, 'maintenance/resident_dashboard.html', context)


@login_required
def create_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.resident = request.user
            complaint.save()
            messages.success(request, f"Complaint registered successfully! Your Ticket ID is {complaint.ticket_id}")
            return redirect('dashboard')
    else:
        form = ComplaintForm()
    return render(request, 'maintenance/create_complaint.html', {'form': form})


@login_required
def complaint_detail(request, ticket_id):
    complaint = get_object_or_404(Complaint, ticket_id=ticket_id)
    otp_form = OTPVerificationForm()
    feedback_form = FeedbackForm()

    context = {
        'complaint': complaint,
        'otp_form': otp_form,
        'feedback_form': feedback_form,
    }
    return render(request, 'maintenance/complaint_detail.html', context)


@login_required
def allocate_job(request, ticket_id):
    complaint = get_object_or_404(Complaint, ticket_id=ticket_id)
    
    if request.user.role not in ['JE_CIVIL', 'JE_ELEC', 'STAFF_OFFICER'] and not request.user.is_superuser:
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = JobAllocationForm(request.POST)
        if form.is_valid():
            allocation, created = JobAllocation.objects.get_or_create(complaint=complaint)
            allocation.assigned_by_je = request.user
            allocation.technician_name = form.cleaned_data['technician_name']
            allocation.technician_phone = form.cleaned_data['technician_phone']
            allocation.target_completion_date = form.cleaned_data['target_completion_date']
            allocation.materials_issued = form.cleaned_data['materials_issued']
            allocation.work_remarks = form.cleaned_data['work_remarks']
            allocation.save()

            complaint.status = 'ASSIGNED'
            complaint.save()
            messages.success(request, f"Job allocated to {allocation.technician_name} for Ticket {complaint.ticket_id}")
            return redirect('complaint_detail', ticket_id=complaint.ticket_id)
    else:
        # Pre-fill if already exists
        initial_data = {}
        if hasattr(complaint, 'allocation'):
            alloc = complaint.allocation
            initial_data = {
                'technician_name': alloc.technician_name,
                'technician_phone': alloc.technician_phone,
                'target_completion_date': alloc.target_completion_date,
                'materials_issued': alloc.materials_issued,
                'work_remarks': alloc.work_remarks,
            }
        form = JobAllocationForm(initial=initial_data)

    return render(request, 'maintenance/allocate_job.html', {'form': form, 'complaint': complaint})


@login_required
def update_status(request, ticket_id, new_status):
    complaint = get_object_or_404(Complaint, ticket_id=ticket_id)
    
    if request.user.role not in ['JE_CIVIL', 'JE_ELEC', 'STAFF_OFFICER'] and not request.user.is_superuser:
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    valid_statuses = ['IN_PROGRESS', 'RESOLVED']
    if new_status in valid_statuses:
        complaint.status = new_status
        if new_status == 'RESOLVED':
            complaint.resolved_at = timezone.now()
        complaint.save()
        messages.success(request, f"Status updated to {complaint.get_status_display()} for Ticket {complaint.ticket_id}")
    
    return redirect('complaint_detail', ticket_id=complaint.ticket_id)


@login_required
def verify_and_close(request, ticket_id):
    complaint = get_object_or_404(Complaint, ticket_id=ticket_id)

    if request.method == 'POST':
        otp_entered = request.POST.get('otp', '').strip()
        rating = request.POST.get('rating')
        comments = request.POST.get('comments', '')

        if otp_entered == complaint.verification_otp:
            complaint.status = 'CLOSED'
            complaint.resolved_at = timezone.now()
            complaint.save()

            if rating:
                Feedback.objects.create(
                    complaint=complaint,
                    rating=int(rating),
                    comments=comments
                )

            messages.success(request, f"Ticket {complaint.ticket_id} verified and closed successfully!")
        else:
            messages.error(request, "Invalid OTP. Please check the 4-digit code provided on the resident dashboard.")

    return redirect('complaint_detail', ticket_id=complaint.ticket_id)
