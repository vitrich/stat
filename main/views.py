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

    # Все ключевые даты
    key_dates = [
        date(2025, 9, 1),
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

        # Последняя дата - когда ученик последний раз был в системе
        last_date = history_sorted[-1]['date']
        last_group = history_sorted[-1]['group']

        # Индекс текущей записи в истории
        history_index = 0
        current_group = first_group

        # Проходим по всем ключевым датам
        for key_date in key_dates:
            # Пропускаем даты до появления ученика
            if key_date < first_date:
                continue

            # Пропускаем даты п
