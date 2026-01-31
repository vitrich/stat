from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


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
    """Ученик"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
    full_name = models.CharField(max_length=200, verbose_name='ФИО', unique=True)
    current_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name='students',
                                      verbose_name='Текущая группа')
    is_registered = models.BooleanField(default=False, verbose_name='Зарегистрирован')
    parent_contact = models.CharField(max_length=200, blank=True, verbose_name='Контакт родителя')

    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


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
