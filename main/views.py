from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentRegistrationForm
from .models import GroupHistory, Student, Group
from collections import defaultdict
import json


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
    """Статистика переходов между группами - интерактивный график"""

    # Получаем всю историю
    all_history = GroupHistory.objects.select_related('student', 'group').order_by('student_id', 'transfer_date')

    # Собираем полную историю для каждого ученика
    students_full_history = defaultdict(list)
    students_info = {}

    for entry in all_history:
        student_id = entry.student.id
        students_full_history[student_id].append({
            'date': entry.transfer_date.strftime('%Y-%m-%d'),
            'group': float(entry.group.number),
            'reason': entry.reason
        })
        if student_id not in students_info:
            students_info[student_id] = {
                'id': student_id,
                'name': entry.student.full_name
            }

    # Группируем по датам
    history_by_date = defaultdict(list)
    for entry in all_history:
        history_by_date[entry.transfer_date].append(entry)

    # Находим переходы (ученики с более чем 1 записью)
    students_with_changes = defaultdict(list)
    for entry in all_history:
        students_with_changes[entry.student.id].append(entry)

    # Собираем список учеников с переходами
    students_with_transitions = []
    for student_id, entries in students_with_changes.items():
        if len(entries) > 1:
            students_with_transitions.append({
                'id': student_id,
                'name': entries[0].student.full_name,
                'history': students_full_history[student_id]
            })

    # Сортируем по имени
    students_with_transitions.sort(key=lambda x: x['name'])

    # Статистика по группам
    groups = Group.objects.all().order_by('number')
    group_stats = []
    for group in groups:
        current_count = Student.objects.filter(current_group=group).count()
        group_stats.append({
            'group': group,
            'current_count': current_count,
            'teacher': group.teacher.full_name if group.teacher else 'Не назначен'
        })

    context = {
        'students_with_transitions': students_with_transitions,
        'students_json': json.dumps({
            s['id']: {
                'name': s['name'],
                'history': s['history']
            } for s in students_with_transitions
        }),
        'group_stats': group_stats,
    }

    return render(request, 'statistics.html', context)


@login_required
def stats_overview(request):
    return render(request, 'statistics.html', {'view': 'overview'})


@login_required
def stats_reports(request):
    return render(request, 'statistics.html', {'view': 'reports'})


@login_required
def stats_analytics(request):
    return render(request, 'statistics.html', {'view': 'analytics'})


# Регистрация
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
