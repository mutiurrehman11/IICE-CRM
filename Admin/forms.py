from django import forms
from authentication.models import User  # Import your User model
from Admin.models import Sessions, Student, Lead, Attendance

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email','password', 'usertype', 'status', 'mobile_no', 'cnic', 'address', 'profile_photo', 'joining_date']

class SessionForm(forms.ModelForm):
    class Meta:
        model = Sessions
        fields = '__all__'
        widgets = {
            'session_type': forms.Select(attrs={'class': 'form-select', 'onchange': 'toggleFeeFields()'}),
            'session_name': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        fee = cleaned_data.get('fee')
        
        if not fee:
            raise forms.ValidationError({'fee': 'Fee is required for all sessions.'})
            
        return cleaned_data

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['created_at', 'rollno', 'added_by']  # Exclude auto-generated fields
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists (excluding current instance if editing)
            existing = Student.objects.filter(email=email)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("A student with this email already exists.")
        return email
        
    def clean_cnic(self):
        cnic = self.cleaned_data.get('cnic')
        if cnic:
            # Remove any non-digit characters for validation
            cnic_digits = ''.join(filter(str.isdigit, cnic))
            if len(cnic_digits) != 13:
                raise forms.ValidationError("CNIC must contain exactly 13 digits.")
        return cnic

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = '__all__'

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['course', 'student', 'date', 'status']