from django.urls import path
from . import views

urlpatterns = [
    path('subject/<int:subject_id>/delete/', views.delete_subject, name='delete_subject'),
]