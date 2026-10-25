import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    """
    Custom user model supporting Employees/Residents, Junior Engineers, 
    and Senior Welfare/Staff Officers.
    """
    ROLE_CHOICES = (
        ('RESIDENT', 'Resident / Employee'),
        ('JE_CIVIL', 'Junior Engineer (Civil)'),
        ('JE_ELEC', 'Junior Engineer (Electrical)'),
        ('STAFF_OFFICER', 'Staff Officer / Town Admin'),
    )

    COLONY_CHOICES = (
        ('GANDHINAGAR', 'Gandhinagar Colony, Ranchi'),
        ('JAWAHARNAGAR', 'Jawaharnagar Colony, Ranchi'),
        ('RAJENDRA_NAGAR', 'Rajendra Nagar Colony, Ranchi'),
        ('PIPARWAR', 'Piparwar Area Colony'),
        ('KATHARA', 'Kathara Area Colony'),
        ('BARKA_SAYAL', 'Barka-Sayal Area Colony'),
    )

    eis_number = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Coal India Employee Identification Number (e.g. EIS-90123456)"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='RESIDENT')
    phone = models.CharField(max_length=15, blank=True, null=True)
    colony_name = models.CharField(max_length=50, choices=COLONY_CHOICES, blank=True, null=True)
    quarter_no = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="e.g. Qtr B-14, Type-III"
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()}) - {self.eis_number}"


class Complaint(models.Model):
    """
    Complaints raised by township residents.
    """
    DEPARTMENT_CHOICES = (
        ('CIVIL', 'Civil Maintenance (Masonry, Roof, Carpentry)'),
        ('ELECTRICAL', 'Electrical Maintenance (Wiring, Meter, Switchboard)'),
        ('WATER_SUPPLY', 'Public Health / Water Supply (Pipes, Taps, Tanks)'),
    )

    PRIORITY_CHOICES = (
        ('NORMAL', 'Normal (Standard 7-Day SLA)'),
        ('EMERGENCY', 'Emergency (Immediate - Pipeline Burst / Power Outage)'),
    )

    STATUS_CHOICES = (
        ('SUBMITTED', 'Submitted'),
        ('ASSIGNED', 'Assigned to Technician'),
        ('IN_PROGRESS', 'Work in Progress'),
        ('RESOLVED', 'Resolved (Awaiting Resident OTP)'),
        ('CLOSED', 'Closed & Verified'),
    )

    ticket_id = models.CharField(max_length=30, unique=True, editable=False)
    resident = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='complaints')
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    issue_type = models.CharField(
        max_length=100, 
        help_text="e.g., Roof Seepage, Broken Switchboard, Main Pipeline Leak"
    )
    description = models.TextField()
    photo = models.ImageField(upload_to='complaints/%Y/%m/', blank=True, null=True)
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default='NORMAL')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    
    # 4-digit verification OTP given to the resident upon resolution
    verification_otp = models.CharField(max_length=6, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Auto-generate a readable Ticket ID if not already present
        if not self.ticket_id:
            year = timezone.now().strftime('%Y')
            rand_code = random.randint(1000, 9999)
            prefix = self.department[:3].upper()
            self.ticket_id = f"CCL-{prefix}-{year}-{rand_code}"
            
            # Generate 4-digit completion verification OTP
            self.verification_otp = str(random.randint(1000, 9999))
            
        super().save(*args, **kwargs)

    @property
    def is_escalated(self):
        """Flag tickets pending more than 7 days as escalated."""
        if self.status not in ['RESOLVED', 'CLOSED']:
            days_open = (timezone.now() - self.created_at).days
            return days_open >= 7
        return False

    def __str__(self):
        return f"[{self.ticket_id}] {self.issue_type} - {self.resident.quarter_no}"


class JobAllocation(models.Model):
    """
    Tracks assignments made by Junior Engineers to contractors/technicians
    and logs materials consumed from departmental stores.
    """
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='allocation')
    assigned_by_je = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'role__in': ['JE_CIVIL', 'JE_ELEC']}
    )
    technician_name = models.CharField(max_length=100)
    technician_phone = models.CharField(max_length=15)
    target_completion_date = models.DateField()
    
    # Tracks inventory usage (prevents material leaks)
    materials_issued = models.TextField(
        blank=True, 
        help_text="e.g., 10m PVC Pipe 1-inch, 1x 16A MCB Switchboard, 1 Bag Cement"
    )
    work_remarks = models.TextField(blank=True)
    allocated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Allocation for {self.complaint.ticket_id} -> {self.technician_name}"


class Feedback(models.Model):
    """
    Resident rating and feedback captured upon ticket closure.
    """
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='feedback')
    rating = models.PositiveSmallIntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)])
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating}★ for {self.complaint.ticket_id}"
