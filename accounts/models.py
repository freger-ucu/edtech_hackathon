from django.db import models
from django.contrib.auth.models import User
import uuid

class Group(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User, related_name='custom_groups')
    share_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return self.name
