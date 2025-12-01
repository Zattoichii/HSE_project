from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    request_count = models.IntegerField(default=0)
    max_requests = models.IntegerField(default=10)
