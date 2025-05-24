from django.contrib import admin
from .models import Group, Subject, Task, Subtask, SubtaskCompletion

# Register your models here.
admin.site.register(Group)
admin.site.register(Subject)
admin.site.register(Task)
admin.site.register(Subtask)
admin.site.register(SubtaskCompletion)
