from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentRegistrationForm
from .models import GroupHistory, Student, Group
from collections import defaultdict
import json
from datetime import date


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

    # АВТОМАТИЧЕСКИ ОПРЕДЕЛЯЕМ ВСЕ УНИКАЛЬНЫЕ ДАТЫ ИЗ БД
    key_dates = list(
        GroupHistory.objects
        .values_list('transfer_date', flat=True)
        .distinct()
        .order_by('transfer_date')
    )

    if not key_dates:
        # Если истории нет, используем дефолтные даты
        key_dates = [
            date(2025, 9, 1),
            date(2025, 10, 15),
            date(2025, 12, 16),
            date(2026, 1, 12)
        ]

    # Получаем всю историю
    all_history = GroupHistory.objects.select_related('student', 'group').order_by('student_id', 'transfer_date')

    # Собираем историю для каждого ученика
    students_history_raw = defaultdict(list)
    students_info = {}

    for entry in all_history:
        student_id = entry.student.id
        students_history_raw[student_id].append({
            'date': entry.transfer_date,
            'group': float(entry.group.number)
        })
        if student_id not in students_info:
            students_info[student_id] = {
                'id': student_id,
                'name': entry.student.full_name
            }

    # Дополняем историю промежуточными точками
    students_full_history = {}

    for student_id, history in students_history_raw.items():
        # Сортируем по дате
        history_sorted = sorted(history, key=lambda x: x['date'])

        # Собираем полную историю с промежуточными точками
        full_history = []

        # Первая дата - когда ученик появился
        first_date = history_sorted[0]['date']
        first_group = history_sorted[0]['group']

        # Индекс текущей записи в истории
        history_index = 0
        current_group = first_group

        # Проходим по всем ключевым датам
        for key_date in key_dates:
            # Пропускаем даты до появления ученика
            if key_date < first_date:
                continue

            # Проверяем, есть ли изменение группы на эту дату
            for i in range(history_index, len(history_sorted)):
                if history_sorted[i]['date'] == key_date:
                    current_group = history_sorted[i]['group']
                    history_index = i + 1
                    break
                elif history_sorted[i]['date'] > key_date:
                    break

            # Добавляем точку на эту дату с текущей группой
            full_history.append({
                'date': key_date.strftime('%Y-%m-%d'),
                'group': current_group
            })

        students_full_history[student_id] = full_history

    # Собираем список учеников с историей
    students_with_transitions = []
    for student_id, history in students_full_history.items():
        if len(history) > 0:
            students_with_transitions.append({
                'id': student_id,
                'name': students_info[student_id]['name'],
                'history': history
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

    # Форматируем даты для отображения
    dates_formatted = [d.strftime('%d.%m.%Y') for d in key_dates]

    context = {
        'students_with_transitions': students_with_transitions,
        'students_json': json.dumps({
            s['id']: {
                'name': s['name'],
                'history': s['history']
            } for s in students_with_transitions
        }),
        'group_stats': group_stats,
        'key_dates': dates_formatted,  # Передаем даты в шаблон
        'dates_count': len(key_dates),  # Количество дат
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
