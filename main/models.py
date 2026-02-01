from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json
import random


class Teacher(models.Model):
    """Преподаватель"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    full_name = models.CharField(max_length=200, verbose_name='ФИО')
    email = models.EmailField(blank=True, null=True)

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

    def __str__(self):
        return self.full_name


class Group(models.Model):
    """Группа"""
    GROUP_CHOICES = [
        (1, 'Группа 1'),
        (2, 'Группа 2'),
        (2.1, 'Группа 2.1'),
        (2.2, 'Группа 2.2'),
        (3, 'Группа 3'),
    ]

    number = models.FloatField(choices=GROUP_CHOICES, unique=True, verbose_name='Номер группы')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='groups',
                                verbose_name='Преподаватель')
    description = models.TextField(blank=True, verbose_name='Описание')
    color = models.CharField(max_length=7, default='#bd2e8d', verbose_name='Цвет для графиков')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['number']

    def __str__(self):
        return f"Группа {self.number}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=200, verbose_name='ФИО')
    class_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Класс')
    current_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name='Текущая группа')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'
        ordering = ['full_name']


class GroupHistory(models.Model):
    """История перемещений по группам"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='group_history', verbose_name='Ученик')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')
    transfer_date = models.DateField(verbose_name='Дата перехода')
    reason = models.TextField(blank=True, verbose_name='Причина перемещения')

    class Meta:
        verbose_name = 'История группы'
        verbose_name_plural = 'История групп'
        ordering = ['-transfer_date']

    def __str__(self):
        return f"{self.student.full_name} → Группа {self.group.number} ({self.transfer_date})"


class Lesson(models.Model):
    """Урок с теоретическим материалом"""
    title = models.CharField(max_length=200, verbose_name='Название урока')
    date = models.DateField(verbose_name='Дата урока')
    subject = models.CharField(max_length=100, default='Математика', verbose_name='Предмет')
    grade = models.CharField(max_length=20, default='5', verbose_name='Класс')

    theory_content = models.TextField(verbose_name='Теоретический материал (HTML)')
    duration_minutes = models.IntegerField(default=40, verbose_name='Длительность урока (минут)')
    test_duration_minutes = models.IntegerField(default=5, verbose_name='Время на тест (минут)')

    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} ({self.date})"


class LessonTask(models.Model):
    """Задание для ученика к конкретному уроку"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='tasks')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='lesson_tasks')

    # Сгенерированные задания (JSON)
    tasks_data = models.TextField(verbose_name='Данные заданий (JSON)')

    # Ответы ученика
    answers = models.TextField(blank=True, null=True, verbose_name='Ответы ученика (JSON)')

    # Результаты
    score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(7)],
        verbose_name='Оценка (0-7)'
    )
    correct_count = models.IntegerField(default=0, verbose_name='Правильных ответов')
    total_count = models.IntegerField(default=10, verbose_name='Всего заданий')

    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='Время сдачи')

    class Meta:
        verbose_name = 'Задание урока'
        verbose_name_plural = 'Задания уроков'
        unique_together = ['lesson', 'student']

    def __str__(self):
        return f"{self.student.full_name} - {self.lesson.title}"

    def generate_tasks(self):
        """Генерация индивидуальных заданий"""
        tasks = []

        # 3 задания на классификацию (правильная/неправильная)
        for _ in range(3):
            numerator = random.randint(1, 20)
            denominator = random.randint(2, 15)
            tasks.append({
                'type': 'classify',
                'numerator': numerator,
                'denominator': denominator,
                'answer': 'proper' if numerator < denominator else 'improper'
            })

        # 3 задания: смешанная → неправильная
        for _ in range(3):
            whole = random.randint(1, 10)
            numerator = random.randint(1, 8)
            denominator = random.randint(2, 9)
            answer_num = whole * denominator + numerator
            tasks.append({
                'type': 'mixed_to_improper',
                'whole': whole,
                'numerator': numerator,
                'denominator': denominator,
                'answer': f"{answer_num}/{denominator}"
            })

        # 4 задания: неправильная → смешанная
        for _ in range(4):
            denominator = random.randint(2, 9)
            whole = random.randint(1, 8)
            numerator = random.randint(1, denominator - 1)
            improper_num = whole * denominator + numerator
            tasks.append({
                'type': 'improper_to_mixed',
                'numerator': improper_num,
                'denominator': denominator,
                'answer': f"{whole} {numerator}/{denominator}"
            })

        self.tasks_data = json.dumps(tasks, ensure_ascii=False)
        self.total_count = len(tasks)
        self.save()

    def check_answers(self, submitted_answers):
        """Проверка ответов и выставление оценки"""
        tasks = json.loads(self.tasks_data)
        correct = 0

        for i, task in enumerate(tasks):
            user_answer = submitted_answers.get(str(i), '').strip()
            correct_answer = task['answer'].strip()

            if user_answer.lower() == correct_answer.lower():
                correct += 1

        self.correct_count = correct
        self.answers = json.dumps(submitted_answers, ensure_ascii=False)
        self.submitted_at = timezone.now()

        # Выставление оценки по 7-бальной системе
        percentage = (correct / len(tasks)) * 100
        if percentage >= 95:
            self.score = 7
        elif percentage >= 85:
            self.score = 6
        elif percentage >= 75:
            self.score = 5
        elif percentage >= 65:
            self.score = 4
        elif percentage >= 50:
            self.score = 3
        elif percentage >= 35:
            self.score = 2
        else:
            self.score = 1

        self.save()
        return self.score


# Старые модели для совместимости
class Assignment(models.Model):
    """Задание (пока заглушка)"""
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='assignments', verbose_name='Группа')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assignments', verbose_name='Создал')
    deadline = models.DateTimeField(verbose_name='Дедлайн')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (Группа {self.group.number})"


class Submission(models.Model):
    """Сданная работа"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions',
                                   verbose_name='Задание')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions', verbose_name='Ученик')
    answer_text = models.TextField(blank=True, verbose_name='Текст ответа')
    file = models.FileField(upload_to='submissions/', blank=True, null=True, verbose_name='Файл')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата сдачи')
    grade = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(7)],
        verbose_name='Оценка (0-7)'
    )
    teacher_comment = models.TextField(blank=True, verbose_name='Комментарий преподавателя')

    class Meta:
        verbose_name = 'Сданная работа'
        verbose_name_plural = 'Сданные работы'
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.full_name} - {self.assignment.title}"
