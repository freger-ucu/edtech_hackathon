from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json
from .models import Group, Subject, Task, Subtask, SubtaskCompletion
from django.urls import reverse
from datetime import date, timedelta
import math

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
    tasks = Task.objects.filter(subject__group__in=groups).order_by('deadline')
    return render(request, 'home.html', {'groups': groups, 'tasks': tasks})

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
    deadlines = Task.objects.filter(subject__group=group).order_by('deadline')
    # Group leaderboard: % of completed subtasks for all users in the group
    all_subtasks = Task.objects.filter(subject__group=group).values_list('subtasks', flat=True)
    all_subtasks = [subtask for subtask in all_subtasks if subtask is not None]
    total = SubtaskCompletion.objects.filter(subtask__in=all_subtasks).count() # Total possible completions across all users and subtasks

    group_leaderboard = []
    for user in group.users.all():
        # Calculate user's completed subtasks within this group's tasks
        user_completed_subtasks = SubtaskCompletion.objects.filter(user=user, subtask__in=all_subtasks).count()
        # Calculate the total number of subtasks in the group for percentage calculation
        total_group_subtasks = Subtask.objects.filter(task__subject__group=group).count()
        
        percent = int((user_completed_subtasks / total_group_subtasks) * 100) if total_group_subtasks > 0 else 0
        green_bars = math.ceil(percent / 5)
        group_leaderboard.append({'user': user, 'percent': percent, 'completed': user_completed_subtasks, 'total': total_group_subtasks, 'green_bars': green_bars})
    group_leaderboard.sort(key=lambda x: x['percent'], reverse=True)

    # --- Streak calculation ---
    streak = 0
    today = date.today()
    group_users = list(group.users.all())
    half_or_more = (len(group_users) + 1) // 2
    streak_done_today = False
    day = today
    streak_completed_users = []
    streak_not_completed_users = []
    while True:
        completions = SubtaskCompletion.objects.filter(
            user__in=group_users,
            subtask__in=all_subtasks,
            completed=True,
            created_at__date=day
        )
        users_done = set(completions.values_list('user_id', flat=True))
        if day == today:
            streak_completed_users = [user for user in group_users if user.id in users_done]
            streak_not_completed_users = [user for user in group_users if user.id not in users_done]
        if len(users_done) >= half_or_more:
            if day == today:
                streak_done_today = True
            streak += 1
            day = day - timedelta(days=1)
        else:
            if day == today:
                streak_done_today = False
            break
    breadcrumbs = [
        {'label': 'Home', 'url': '/'},
        {'label': group.name, 'url': reverse('group_detail', args=[group.id])},
    ]
    context = {
        'group': group,
        'share_link': share_link,
        'deadlines': deadlines,
        'group_leaderboard': group_leaderboard,
        'streak': streak,
        'streak_done_today': streak_done_today,
        'streak_completed_users': streak_completed_users,
        'streak_not_completed_users': streak_not_completed_users,
        'breadcrumbs': breadcrumbs,
        'range_20': range(1, 21),
    }
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

@login_required
def create_subject(request, group_id):
    group = Group.objects.get(id=group_id)
    if request.user not in group.users.all():
        return redirect('home')
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Subject.objects.create(name=name, group=group)
    return redirect('group_detail', group_id=group.id)

@login_required
def delete_subject(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    group_id = subject.group.id
    if request.user in subject.group.users.all():
        subject.delete()
    return redirect('group_detail', group_id=group_id)

@login_required
def subject_detail(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    group = subject.group
    if request.user not in group.users.all():
        return redirect('home')
    if request.method == 'POST' and 'create_task' in request.POST:
        name = request.POST.get('name')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        if name:
            Task.objects.create(name=name, description=description, deadline=deadline, subject=subject)
    tasks = subject.tasks.all()
    subject_deadlines = tasks.order_by('deadline')
    # Subject leaderboard: % of completed subtasks for all users in the group for this subject
    all_subtasks = Subtask.objects.filter(task__subject=subject)
    subject_leaderboard = []
    total = all_subtasks.count()
    for user in group.users.all():
        completed = SubtaskCompletion.objects.filter(user=user, subtask__in=all_subtasks).count()
        percent = int((completed / total) * 100) if total > 0 else 0
        subject_leaderboard.append({'user': user, 'percent': percent, 'completed': completed, 'total': total})
    subject_leaderboard.sort(key=lambda x: x['percent'], reverse=True)
    breadcrumbs = [
        {'label': 'Home', 'url': '/'},
        {'label': group.name, 'url': reverse('group_detail', args=[group.id])},
        {'label': subject.name, 'url': reverse('subject_detail', args=[subject.id])},
    ]
    return render(request, 'subject_detail.html', {'subject': subject, 'tasks': tasks, 'subject_leaderboard': subject_leaderboard, 'subject_deadlines': subject_deadlines, 'breadcrumbs': breadcrumbs})

@login_required
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    subject_id = task.subject.id
    if request.user in task.subject.group.users.all():
        task.delete()
    return redirect('subject_detail', subject_id=subject_id)

@login_required
def task_detail(request, task_id):
    task = Task.objects.get(id=task_id)
    subject = task.subject
    group = subject.group
    if request.user not in group.users.all():
        return redirect('home')
    # Toggle subtask completion
    if request.method == 'POST' and 'toggle_subtask' in request.POST:
        subtask_id = request.POST.get('toggle_subtask')
        subtask = Subtask.objects.get(id=subtask_id)
        completion, created = SubtaskCompletion.objects.get_or_create(user=request.user, subtask=subtask)
        if not created:
            completion.delete()
    if request.method == 'POST' and 'create_subtask' in request.POST:
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            Subtask.objects.create(name=name, description=description, task=task)
    subtasks = task.subtasks.all()
    # Leaderboard: user -> % of completed subtasks for this task
    leaderboard = []
    users = group.users.all()
    total = subtasks.count()
    for user in users:
        completed = SubtaskCompletion.objects.filter(user=user, subtask__in=subtasks).count()
        percent = int((completed / total) * 100) if total > 0 else 0
        leaderboard.append({'user': user, 'percent': percent, 'completed': completed, 'total': total})
    leaderboard.sort(key=lambda x: x['percent'], reverse=True)
    # For current user: set of completed subtask ids
    completed_subtasks = set(SubtaskCompletion.objects.filter(user=request.user, subtask__in=subtasks).values_list('subtask_id', flat=True))
    breadcrumbs = [
        {'label': 'Home', 'url': '/'},
        {'label': group.name, 'url': reverse('group_detail', args=[group.id])},
        {'label': subject.name, 'url': reverse('subject_detail', args=[subject.id])},
        {'label': task.name, 'url': reverse('task_detail', args=[task.id])},
    ]
    return render(request, 'task_detail.html', {'task': task, 'subtasks': subtasks, 'leaderboard': leaderboard, 'completed_subtasks': completed_subtasks, 'breadcrumbs': breadcrumbs})

@login_required
def delete_subtask(request, subtask_id):
    subtask = Subtask.objects.get(id=subtask_id)
    task_id = subtask.task.id
    if request.user in subtask.task.subject.group.users.all():
        subtask.delete()
    return redirect('task_detail', task_id=task_id)
