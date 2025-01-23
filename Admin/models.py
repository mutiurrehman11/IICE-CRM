import os
from django.db import models
from django.utils.text import slugify
from authentication.models import User

def student_profile_photo_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{slugify(instance.student_name)}_{slugify(instance.email)}.{extension}"
    return filename

def student_cnic_photo_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{slugify(instance.student_name)}_{slugify(instance.email)}.{extension}"
    return filename

def student_degree_photo_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{slugify(instance.student_name)}_{slugify(instance.email)}.{extension}"
    return filename


def session_photo_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{slugify(instance.session_name)}.{extension}"
    return filename


class Student(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    rollno = models.CharField(max_length=100, blank=True, null=True)
    student_name = models.CharField(max_length=50,blank=True, null=True)
    father_name = models.CharField(max_length=50,blank=True, null=True)
    email = models.EmailField(unique=True,blank=True, null=True)
    cnic = models.CharField(max_length=15,blank=True, null=True)
    profile_photo = models.ImageField(upload_to=student_profile_photo_path, blank=True, null=True)
    cnic_photo = models.ImageField(upload_to=student_cnic_photo_path, blank=True, null=True)
    degree_photo = models.ImageField(upload_to=student_degree_photo_path, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    mobile_no = models.CharField(max_length=15, blank=True, null=True)  # New field for mobile number
    last_degree = models.CharField(max_length=50,blank=True, null=True)
    last_institution = models.CharField(max_length=50,blank=True, null=True)
    Temp_address = models.TextField(blank=True, null=True)
    Perm_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student_name}"


class Sessions(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    session_name = models.CharField(max_length=50)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    session_photo = models.ImageField(upload_to=session_photo_path, blank=True, null=True)
    registration_fee = models.IntegerField()
    fee = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"{self.session_name}"


class StudentSession(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_sessions')
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE, related_name='session_students')
    registration_date = models.DateField(null=True, blank=True)
    registration_fee = models.IntegerField(null=True, blank=True)
    fee = models.IntegerField(null=True, blank=True)
    fee_paid = models.IntegerField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.session}"


class Lead(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, blank=True, null=True)
    mobile_no = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

class Payments(models.Model):
    studentsession = models.ForeignKey(StudentSession, on_delete=models.CASCADE, related_name='student_payments')
    user = models.ForeignKey(User,on_delete=models.CASCADE ,related_name='payments')
    amount = models.IntegerField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]

    course = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

class Notification(models.Model):
    CATEGORIES = [
        ('General', 'General'),
        ('Late Fee', 'Late fee'),
        ('New Entry', 'New Entry'),
        ('Deletion', 'Deletion'),
        ('New Fee', 'New Fee'),
        ('Updation', 'Updation'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    date = models.DateField()
    category = models.CharField(max_length=10, choices=CATEGORIES)
    content = models.TextField(max_length=200, blank=True, null=True)