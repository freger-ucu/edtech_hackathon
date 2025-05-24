from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json
from .models import Group
from django.urls import reverse

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
    if request.user.is_authenticated:
        return redirect('home')
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
    if request.user.is_authenticated:
        return redirect('home')
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
                    return redirect('home')
                else:
                    context['error'] = 'Invalid credentials.'
            else:
                context['error'] = 'Invalid credentials.'
    return render(request, 'signin.html', context)

def home(request):
    if not request.user.is_authenticated:
        return redirect('signin_page')
    groups = request.user.custom_groups.all()
    return render(request, 'home.html', {'groups': groups})

def logout_view(request):
    auth_logout(request)
    return redirect('signin_page')

@login_required
def create_group(request):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            context['error'] = 'Name is required.'
        else:
            group = Group.objects.create(name=name)
            group.users.add(request.user)
            return redirect('group_detail', group_id=group.id)
    return render(request, 'create_group.html', context)

@login_required
def group_detail(request, group_id):
    group = Group.objects.get(id=group_id)
    if request.user not in group.users.all():
        return redirect('home')
    share_link = request.build_absolute_uri(reverse('group_join', args=[group.share_uuid]))
    context = {'group': group, 'share_link': share_link}
    if request.method == 'POST' and 'leave' in request.POST:
        group.users.remove(request.user)
        return redirect('home')
    return render(request, 'group_detail.html', context)

@login_required
def group_join(request, share_uuid):
    try:
        group = Group.objects.get(share_uuid=share_uuid)
    except Group.DoesNotExist:
        return redirect('home')
    group.users.add(request.user)
    return redirect('group_detail', group_id=group.id)
