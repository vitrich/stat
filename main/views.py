from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentRegistrationForm
from .models import GroupHistory, Student, Group
from collections import defaultdict


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
    """Статистика переходов между группами"""

    # Получаем все переходы
    all_history = GroupHistory.objects.select_related('student', 'group').order_by('transfer_date',
                                                                                   'student__full_name')

    # Группируем по датам
    history_by_date = defaultdict(list)
    for entry in all_history:
        history_by_date[entry.transfer_date].append(entry)

    # Находим переходы (ученики с более чем 1 записью)
    students_with_changes = defaultdict(list)
    for entry in all_history:
        students_with_changes[entry.student.id].append(entry)

    # Оставляем только тех, у кого есть переходы
    transitions = []
    for student_id, entries in students_with_changes.items():
        if len(entries) > 1:
            # Сортируем по дате
            entries_sorted = sorted(entries, key=lambda x: x.transfer_date)
            for i in range(len(entries_sorted) - 1):
                old_entry = entries_sorted[i]
                new_entry = entries_sorted[i + 1]
                transitions.append({
                    'student': old_entry.student,
                    'from_group': old_entry.group,
                    'to_group': new_entry.group,
                    'date': new_entry.transfer_date,
                    'reason': new_entry.reason
                })

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

    # Статистика переходов по направлениям
    transitions_by_direction = defaultdict(int)
    for t in transitions:
        key = f"{t['from_group'].number} → {t['to_group'].number}"
        transitions_by_direction[key] += 1

    context = {
        'history_by_date': dict(history_by_date),
        'transitions': transitions,
        'group_stats': group_stats,
        'transitions_by_direction': dict(transitions_by_direction),
        'total_transitions': len(transitions),
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
