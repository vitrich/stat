from fractions import Fraction
from datetime import date
import json
from collections import defaultdict

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages

from .forms import StudentRegistrationForm
from .models import GroupHistory, Student, Group, Lesson, LessonTask


def _normalize_fraction(s: str):
    s = (s or "").strip().replace(" ", "")
    if "/" not in s:
        return None
    try:
        p, q = s.split("/", 1)
        return Fraction(int(p), int(q))
    except Exception:
        return None


def _is_correct_for_task(task: dict, useranswer: str, correctanswer: str) -> bool:
    t = (task.get("type") or "").strip()
    ua = (useranswer or "").strip()
    ca = (correctanswer or "").strip()

    # Урок 3: дроби — принимаем эквивалентные ответы
    if t in ("add_diff", "sub_diff"):
        f_ua = _normalize_fraction(ua)
        f_ca = _normalize_fraction(ca)
        return (f_ua is not None and f_ca is not None and f_ua == f_ca)

    # Урок 3: общий знаменатель — две дроби через запятую
    if t == "common_denom":
        parts_u = [p.strip() for p in (ua or "").split(",")]
        parts_c = [p.strip() for p in (ca or "").split(",")]
        if len(parts_u) != 2 or len(parts_c) != 2:
            return False
        u1 = _normalize_fraction(parts_u[0])
        u2 = _normalize_fraction(parts_u[1])
        c1 = _normalize_fraction(parts_c[0])
        c2 = _normalize_fraction(parts_c[1])
        return (u1 == c1 and u2 == c2)

    # Сравнение дробей — строго символы > < =
    if t in ("comparesamedenom", "comparediffdenom"):
        return ua.replace(" ", "") == ca.replace(" ", "")

    # Остальное — сравнение строк
    return ua.lower() == ca.lower()


def home(request):
    context = {}

    if request.user.is_authenticated:
        try:
            student = request.user.student
            lessons = Lesson.objects.filter(isactive=True).order_by('date')

            lessons_with_status = []
            completed_count = 0

            for lesson in lessons:
                try:
                    lessontask = LessonTask.objects.get(lesson=lesson, student=student)
                    lesson.completed = lessontask.submittedat is not None
                    lesson.score = lessontask.score if lessontask.submittedat else None
                    if lesson.completed:
                        completed_count += 1
                except LessonTask.DoesNotExist:
                    lesson.completed = False
                    lesson.score = None

                lessons_with_status.append(lesson)

            context['lessons'] = lessons_with_status
            context['student'] = student
            context['completedcount'] = completed_count
            context['totallessons'] = len(lessons_with_status)

        except Student.DoesNotExist:
            pass

    return render(request, 'home.html', context)


def news(request):
    return render(request, 'news.html')


def newsarchive(request):
    return render(request, 'news.html', {'archive': True})


@login_required
def lessonview(request, lessondate):
    try:
        lesson = get_object_or_404(Lesson, date=lessondate, isactive=True)

        try:
            student = request.user.student
        except Student.DoesNotExist:
            messages.error(request, 'Только ученики могут проходить уроки.')
            return redirect('home')

        lessontask, created = LessonTask.objects.get_or_create(lesson=lesson, student=student)

        if created or not lessontask.tasksdata:
            lessontask.generate_tasks()

        tasks = json.loads(lessontask.tasksdata)

        if request.method == 'POST':
            if lessontask.submittedat:
                messages.warning(request, 'Тест уже был отправлен!')
                return redirect('lessonresult', lessondate=lessondate)

            answers = {}
            for i in range(len(tasks)):
                answer = (request.POST.get(f'answer_{i}', '') or '').strip()
                answers[str(i)] = answer

            score = lessontask.check_answers(answers)
            messages.success(request, f'Тест отправлен! Ваша оценка: {score} из 7')
            return redirect('lessonresult', lessondate=lessondate)

        context = {
            'lesson': lesson,
            'lessontask': lessontask,
            'tasks': tasks,
            'alreadysubmitted': lessontask.submittedat is not None
        }
        return render(request, 'lesson.html', context)

    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('home')


@login_required
def lessonresult(request, lessondate):
    lesson = get_object_or_404(Lesson, date=lessondate)

    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Только ученики могут смотреть результаты урока.')
        return redirect('home')

    lessontask = get_object_or_404(LessonTask, lesson=lesson, student=student)

    if not lessontask.submittedat:
        messages.warning(request, 'Сначала нужно пройти тест!')
        return redirect('lessonview', lessondate=lessondate)

    tasks = json.loads(lessontask.tasksdata)
    answers = json.loads(lessontask.answers) if lessontask.answers else {}

    results = []
    for i, task in enumerate(tasks):
        useranswer = (answers.get(str(i), "") or "").strip()
        correctanswer = (task.get("answer", "") or "").strip()
        iscorrect = _is_correct_for_task(task, useranswer, correctanswer)

        results.append({
            'task': task,
            'useranswer': useranswer,
            'correctanswer': correctanswer,
            'iscorrect': iscorrect
        })

    context = {
        'lesson': lesson,
        'lessontask': lessontask,
        'results': results
    }
    return render(request, 'lesson_result.html', context)


@login_required
def tasks(request):
    return render(request, 'tasks.html')


@login_required
def tasksactive(request):
    return render(request, 'tasks.html', {'filter': 'active'})


@login_required
def taskscompleted(request):
    return render(request, 'tasks.html', {'filter': 'completed'})


@login_required
def taskscreate(request):
    return render(request, 'tasks.html', {'mode': 'create'})


def isteacher(user):
    try:
        return hasattr(user, 'teacherprofile')
    except Exception:
        return False


@login_required
def students(request):
    if not isteacher(request.user):
        messages.error(request, 'Доступ только для учителей.')
        return redirect('home')

    teacher = request.user.teacherprofile
    teachergroups = teacher.groups.all()

    studentslist = Student.objects.filter(currentgroup__in=teachergroups).order_by('fullname')
    lessons = Lesson.objects.filter(isactive=True).order_by('date')

    resultstable = []
    for student in studentslist:
        studentdata = {'student': student, 'results': []}
        for lesson in lessons:
            try:
                task = LessonTask.objects.get(lesson=lesson, student=student)
                if task.submittedat:
                    studentdata['results'].append({'lesson': lesson, 'score': task.score, 'submitted': True})
                else:
                    studentdata['results'].append({'lesson': lesson, 'score': None, 'submitted': False})
            except LessonTask.DoesNotExist:
                studentdata['results'].append({'lesson': lesson, 'score': None, 'submitted': False})
        resultstable.append(studentdata)

    context = {
        'resultstable': resultstable,
        'lessons': lessons,
        'teachergroups': teachergroups
    }
    return render(request, 'students.html', context)


@login_required
def studentslist(request):
    return render(request, 'students.html', {'view': 'list'})


@login_required
def studentsgroups(request):
    return render(request, 'students.html', {'view': 'groups'})


@login_required
def studentsprogress(request):
    return render(request, 'students.html', {'view': 'progress'})


@login_required
def statistics(request):
    if not isteacher(request.user):
        messages.error(request, 'Доступ только для учителей.')
        return redirect('home')

    keydates = list(
        GroupHistory.objects
        .values_list('transferdate', flat=True)
        .distinct()
        .order_by('transferdate')
    )

    if not keydates:
        keydates = [
            date(2025, 9, 1),
            date(2025, 10, 15),
            date(2025, 12, 16),
            date(2026, 1, 12),
        ]

    allhistory = GroupHistory.objects.select_related('student', 'group').order_by('student_id', 'transferdate')

    studentshistoryraw = defaultdict(list)
    studentsinfo = {}

    for entry in allhistory:
        studentid = entry.student.id
        studentshistoryraw[studentid].append({
            'date': entry.transferdate,
            'group': float(entry.group.number)
        })
        if studentid not in studentsinfo:
            studentsinfo[studentid] = {'id': studentid, 'name': entry.student.fullname}

    studentsfullhistory = {}
    for studentid, history in studentshistoryraw.items():
        historysorted = sorted(history, key=lambda x: x['date'])
        if not historysorted:
            continue

        firstdate = historysorted[0]['date']
        currentgroup = historysorted[0]['group']
        historyindex = 0

        fullhistory = []
        for keydate in keydates:
            if keydate < firstdate:
                continue

            for i in range(historyindex, len(historysorted)):
                if historysorted[i]['date'] <= keydate:
                    currentgroup = historysorted[i]['group']
                    historyindex = i + 1
                else:
                    break

            fullhistory.append({
                'date': keydate.strftime("%Y-%m-%d"),
                'group': currentgroup
            })

        studentsfullhistory[studentid] = fullhistory

    studentswithtransitions = []
    for studentid, history in studentsfullhistory.items():
        if history:
            studentswithtransitions.append({
                'id': studentid,
                'name': studentsinfo.get(studentid, {}).get('name', '—'),
                'history': history
            })

    groups = Group.objects.all().order_by('number')
    groupstats = []
    for group in groups:
        currentcount = Student.objects.filter(currentgroup=group).count()
        groupstats.append({
            'group': group,
            'currentcount': currentcount,
            'teacher': group.teacher.fullname if group.teacher else '—'
        })

    datesformatted = [d.strftime("%d.%m.%Y") for d in keydates]

    context = {
        'studentswithtransitions': studentswithtransitions,
        'studentsjson': json.dumps(
            [{'id': s['id'], 'name': s['name'], 'history': s['history']} for s in studentswithtransitions],
            ensure_ascii=False
        ),
        'groupstats': groupstats,
        'keydates': datesformatted,
        'datescount': len(keydates),
    }
    return render(request, 'statistics.html', context)


@login_required
def statsoverview(request):
    if not isteacher(request.user):
        messages.error(request, 'Доступ только для учителей.')
        return redirect('home')
    return render(request, 'statistics.html', {'view': 'overview'})


@login_required
def statsreports(request):
    if not isteacher(request.user):
        messages.error(request, 'Доступ только для учителей.')
        return redirect('home')
    return render(request, 'statistics.html', {'view': 'reports'})


@login_required
def statsanalytics(request):
    if not isteacher(request.user):
        messages.error(request, 'Доступ только для учителей.')
        return redirect('home')
    return render(request, 'statistics.html', {'view': 'analytics'})


def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            student = form.cleaned_data['student']
            login(request, user)
            messages.success(request, f'Добро пожаловать, {student.fullname}!')
            return redirect('home')
    else:
        form = StudentRegistrationForm()

    return render(request, 'register.html', {'form': form})


# --- aliases for urls.py names (underscore style) ---
news_archive = newsarchive

tasks_active = tasksactive
tasks_completed = taskscompleted
tasks_create = taskscreate

lesson_view = lessonview
lesson_result = lessonresult

students_list = studentslist
students_groups = studentsgroups
students_progress = studentsprogress

stats_overview = statsoverview
stats_reports = statsreports
stats_analytics = statsanalytics
