import os
from django.db import models
from django.utils.text import slugify

def student_profile_photo_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{slugify(instance.first_name)}_{slugify(instance.last_name)}_{slugify(instance.email)}.{extension}"
    return os.path.join('Pictures/Student', filename)


class Student(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    student_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    cnic = models.CharField(max_length=15)
    profile_photo = models.ImageField(upload_to=student_profile_photo_path, blank=True, null=True)
    cnic_photo = models.ImageField(upload_to=student_profile_photo_path, blank=True, null=True)
    degree_photo = models.ImageField(upload_to=student_profile_photo_path, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    mobile_no = models.CharField(max_length=15, blank=True, null=True)  # New field for mobile number
    last_degree = models.CharField(max_length=50)
    last_institution = models.CharField(max_length=50)
    Temp_address = models.TextField(blank=True, null=True)  # New field for address
    Perm_address = models.TextField(blank=True, null=True)  # New field for address


class Sessions(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    session_name = models.CharField(max_length=50)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    registration_fee = models.IntegerField()
    fee = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')