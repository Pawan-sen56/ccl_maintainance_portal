from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Complaint, JobAllocation, Feedback


class CustomUserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'eis_number', 'first_name', 'last_name', 'email', 'phone', 'role', 'colony_name', 'quarter_no')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'eis_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. EIS-90123456'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Official Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'colony_name': forms.Select(attrs={'class': 'form-select'}),
            'quarter_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Qtr B-14, Type-III'}),
        }


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ('department', 'issue_type', 'description', 'priority', 'photo')
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'issue_type': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Brief summary (e.g. Roof seepage in master bedroom, Main water tap broken)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Provide detailed location and issue details...'
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class JobAllocationForm(forms.ModelForm):
    class Meta:
        model = JobAllocation
        fields = ('technician_name', 'technician_phone', 'target_completion_date', 'materials_issued', 'work_remarks')
        widgets = {
            'technician_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Technician or Contractor Name'}),
            'technician_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Technician Contact Number'}),
            'target_completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'materials_issued': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'e.g. 10m PVC Pipe 1-inch, 1x 16A MCB, 1 Bag Cement'
            }),
            'work_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Internal notes...'}),
        }


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6, 
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center fs-4 tracking-widest', 
            'placeholder': '4-Digit OTP'
        })
    )


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('rating', 'comments')
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'How was the repair work completed?'
            }),
        }
