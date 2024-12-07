import os
from django.db import models
from django.utils.text import slugify

def profile_photo_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{slugify(instance.first_name)}_{slugify(instance.last_name)}_{slugify(instance.email)}.{extension}"
    return filename


class User(models.Model):
    USER_TYPE_CHOICES = [
        (1, 'Admin'),
        (2, 'Moderator'),
        (3, 'Teacher'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to=profile_photo_path, blank=True, null=True)
    usertype = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=3)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    mobile_no = models.CharField(max_length=15, blank=True, null=True)  # New field for mobile number
    cnic = models.CharField(max_length=15, blank=True, null=True)  # New field for mobile number
    address = models.TextField(blank=True, null=True)  # New field for address
    joining_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


