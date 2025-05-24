from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        password2 = data.get('password2')

        if not all([username, email, password, password2]):
            return JsonResponse({'error': 'All fields are required.'}, status=400)
        if password != password2:
            return JsonResponse({'error': 'Passwords do not match.'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists.'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists.'}, status=400)
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return JsonResponse({'success': 'Account created successfully.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def signin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        if not all([email, password]):
            return JsonResponse({'error': 'Email and password are required.'}, status=400)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid credentials.'}, status=400)
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': 'Signed in successfully.'})
        else:
            return JsonResponse({'error': 'Invalid credentials.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def signup_page(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if not all([username, email, password, password2]):
            context['error'] = 'All fields are required.'
        elif password != password2:
            context['error'] = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            context['error'] = 'Username already exists.'
        elif User.objects.filter(email=email).exists():
            context['error'] = 'Email already exists.'
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            context['success'] = 'Account created successfully.'
    return render(request, 'signup.html', context)

def signin_page(request):
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not all([email, password]):
            context['error'] = 'Email and password are required.'
        else:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None
            if user:
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    context['success'] = 'Signed in successfully.'
                else:
                    context['error'] = 'Invalid credentials.'
            else:
                context['error'] = 'Invalid credentials.'
    return render(request, 'signin.html', context)
