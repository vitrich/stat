from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import StudentRegistrationForm
from .models import GroupHistory, Student, Group, Lesson, LessonTask, Teacher
from collections import defaultdict
import json
from datetime import date


def home(request):
    context = {}

    # Если пользователь авторизован и является учеником
    if request.user.is_authenticated:
        try:
            student = request.user.student

            # Получаем все активные уроки
            lessons = Lesson.objects.filter(is_active=True).order_by('-date')

            # Проверяем статус выполнения каждого урока
            lessons_with_status = []
            for lesson in lessons:
                try:
                    lesson_task = LessonTask.objects.get(lesson=lesson, student=student)
                    lesson.completed = lesson_task.submitted_at is not None
                except LessonTask.DoesNotExist:
                    lesson.completed = False

                lessons_with_status.append(lesson)

            context['lessons'] = lessons_with_status

        except Student.DoesNotExist:
            # Пользователь не ученик (возможно, преподаватель)
            pass

    return render(request, 'home.html', context)


# Новости
def news(request):
    return render(request, 'news.html')


def news_archive(request):
    return render(request, 'news.html', {'archive': True})


# Уроки математики
@login_required
def lesson_view(request, lesson_date):
    """Просмотр урока и выполнение заданий"""
    try:
        # Получаем урок по дате
        lesson = get_object_or_404(Lesson, date=lesson_date, is_active=True)

        # Получаем ученика
        try:
            student = request.user.student
        except Student.DoesNotExist:
            messages.error(request, 'Ваш профиль ученика не найден.')
            return redirect('home')

        # Получаем или создаем задание для ученика
        lesson_task, created = LessonTask.objects.get_or_create(
            lesson=lesson,
            student=student
        )

        # Если задание новое, генерируем задачи
        if created or not lesson_task.tasks_data:
            lesson_task.generate_tasks()

        # Загружаем задания
        tasks = json.loads(lesson_task.tasks_data)

        # Обработка отправки формы
        if request.method == 'POST':
            if lesson_task.submitted_at:
                messages.warning(request, 'Вы уже сдали этот тест!')
                return redirect('lesson_result', lesson_date=lesson_date)

            # Собираем ответы
            answers = {}
            for i in range(len(tasks)):
                answer = request.POST.get(f'answer_{i}', '').strip()
                answers[str(i)] = answer

            # Проверяем и выставляем оценку
            score = lesson_task.check_answers(answers)

            messages.success(request, f'Тест сдан! Ваша оценка: {score} из 7')
            return redirect('lesson_result', lesson_date=lesson_date)

        context = {
            'lesson': lesson,
            'lesson_task': lesson_task,
            'tasks': tasks,
            'already_submitted': lesson_task.submitted_at is not None
        }

        return render(request, 'lesson.html', context)

    except Exception as e:
        messages.error(request, f'Ошибка загрузки урока: {str(e)}')
        return redirect('home')


@login_required
def lesson_result(request, lesson_date):
    """Результаты выполнения урока"""
    lesson = get_object_or_404(Lesson, date=lesson_date)

    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Ваш профиль ученика не найден.')
        return redirect('home')

    lesson_task = get_object_or_404(LessonTask, lesson=lesson, student=student)

    if not lesson_task.submitted_at:
        messages.warning(request, 'Сначала выполните тест!')
        return redirect('lesson_view', lesson_date=lesson_date)

    tasks = json.loads(lesson_task.tasks_data)
    answers = json.loads(lesson_task.answers) if lesson_task.answers else {}

    # Формируем детальные результаты
    results = []
    for i, task in enumerate(tasks):
        user_answer = answers.get(str(i), '')
        correct_answer = task['answer']
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

        results.append({
            'task': task,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct
        })

    context = {
        'lesson': lesson,
        'lesson_task': lesson_task,
        'results': results
    }

    return render(request, 'lesson_result.html', context)


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


# Проверка: является ли пользователь преподавателем
def is_teacher(user):
    try:
        return hasattr(user, 'teacher_profile')
    except:
        return False


# Статистика - ТОЛЬКО ДЛЯ ПРЕПОДАВАТЕЛЕЙ
@login_required
def statistics(request):
    """Статистика переходов между группами - интерактивный график (только для преподавателей)"""

    # Проверка прав доступа
    if not is_teacher(request.user):
        messages.error(request, 'У вас нет доступа к этому разделу. Статистика доступна только преподавателям.')
        return redirect('home')

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
        'key_dates': dates_formatted,
        'dates_count': len(key_dates),
    }

    return render(request, 'statistics.html', context)


@login_required
def stats_overview(request):
    # Проверка прав доступа
    if not is_teacher(request.user):
        messages.error(request, 'У вас нет доступа к этому разделу.')
        return redirect('home')
    return render(request, 'statistics.html', {'view': 'overview'})


@login_required
def stats_reports(request):
    # Проверка прав доступа
    if not is_teacher(request.user):
        messages.error(request, 'У вас нет доступа к этому разделу.')
        return redirect('home')
    return render(request, 'statistics.html', {'view': 'reports'})


@login_required
def stats_analytics(request):
    # Проверка прав доступа
    if not is_teacher(request.user):
        messages.error(request, 'У вас нет доступа к этому разделу.')
        return redirect('home')
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
