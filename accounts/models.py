from django.db import models
from django.contrib.auth.models import User
import uuid

class Group(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User, related_name='custom_groups')
    share_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=255)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return self.name

class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='tasks')
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class Subtask(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')

    def __str__(self):
        return self.name
