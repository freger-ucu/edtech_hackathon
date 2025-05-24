from django.urls import path
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path('accounts/login/', lambda request: redirect('signin_page', permanent=True)),
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_page, name='signup_page'),
    path('signin/', views.signin_page, name='signin_page'),
    path('create_group/', views.create_group, name='create_group'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('group/<int:group_id>/create_subject/', views.create_subject, name='create_subject'),
    path('subject/<int:subject_id>/delete/', views.delete_subject, name='delete_subject'),
    path('subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('subject/<int:subject_id>/create_task/', views.create_task_for_subject, name='create_task_for_subject'),
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('subtask/<int:subtask_id>/delete/', views.delete_subtask, name='delete_subtask'),
    path('join/<uuid:share_uuid>/', views.group_join, name='group_join'),
    path('api/signup/', views.signup, name='signup'),
    path('api/signin/', views.signin, name='signin'),
] 