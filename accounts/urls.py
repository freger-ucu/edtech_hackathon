from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_page, name='signup_page'),
    path('signin/', views.signin_page, name='signin_page'),
    path('api/signup/', views.signup, name='signup'),
    path('api/signin/', views.signin, name='signin'),
] 