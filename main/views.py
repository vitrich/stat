from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentRegistrationForm


def home(request):
    return render(request, 'home.html')


# Новости
def news(request):
    return render(request, 'news.html')


def news_archive(request):
    return render(request, 'news.html', {'archive': True})


# Задачи
@login_required
def tasks(request):
    return render(request, 'tasks.html')


@login_required
def tasks_active(request):
    return render(request, 'tasks.html', {'filter': 'active'})


@login_required
def tasks_completed(request):
    return render(request, 'tasks.html', {'filter': 'completed'})


@login_required
def tasks_create(request):
    return render(request, 'tasks.html', {'mode': 'create'})


# Ученики
@login_required
def students(request):
    return render(request, 'students.html')


@login_required
def students_list(request):
    return render(request, 'students.html', {'view': 'list'})


@login_required
def students_groups(request):
    return render(request, 'students.html', {'view': 'groups'})


@login_required
def students_progress(request):
    return render(request, 'students.html', {'view': 'progress'})


# Статистика
@login_required
def statistics(request):
    return render(request, 'statistics.html')


@login_required
def stats_overview(request):
    return render(request, 'statistics.html', {'view': 'overview'})


@login_required
def stats_reports(request):
    return render(request, 'statistics.html', {'view': 'reports'})


@login_required
def stats_analytics(request):
    return render(request, 'statistics.html', {'view': 'analytics'})


# Регистрация (ОБНОВЛЕНО)
def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            student = form.cleaned_data['student']
            messages.success(request, f'Регистрация успешна! Добро пожаловать, {student.full_name}!')
            return redirect('login')
    else:
        form = StudentRegistrationForm()

    return render(request, 'register.html', {'form': form})
