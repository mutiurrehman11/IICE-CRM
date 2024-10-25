from django import forms
from authentication.models import User  # Import your User model

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email','password', 'usertype', 'status', 'mobile_no', 'cnic', 'address', 'profile_photo', 'joining_date']
