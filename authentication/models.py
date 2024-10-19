import os
from django.db import models
from django.utils.text import slugify


def profile_photo_path(instance, filename):
    # Get the file extension (e.g., '.jpg', '.png')
    extension = filename.split('.')[-1]

    # Create a new file name using the user's first and last name, and append the extension
    filename = f"{slugify(instance.first_name)}_{slugify(instance.last_name)}_{slugify(instance.email)}.{extension}"

    # Return the custom path where the image will be stored
    return os.path.join('Pictures/Profile', filename)


class User(models.Model):
    USER_TYPE_CHOICES = [
        (1, 'Admin'),
        (2, 'Moderator'),
        (3, 'Teacher'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to=profile_photo_path, blank=True, null=True)
    usertype = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=3)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
