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

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = '__all__'


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['course', 'student', 'date', 'status']