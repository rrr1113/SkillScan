from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        default='profile_photos/default.jpg',
        blank=True
    )
    phone_number = models.CharField(null=True, blank=True, max_length=20)