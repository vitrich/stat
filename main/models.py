from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json
import random
from fractions import Fraction


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
        # Определяем тип урока по дате или названию
        lesson_date_str = str(self.lesson.date)
        
        if '2026-02-03' in lesson_date_str or 'сравнение' in self.lesson.title.lower():
            # УРОК 2: Сравнение и сокращение дробей
            tasks = self._generate_comparison_tasks()
        else:
            # УРОК 1: Смешанные и неправильные дроби (по умолчанию)
            tasks = self._generate_mixed_fraction_tasks()
        
        self.tasks_data = json.dumps(tasks, ensure_ascii=False)
        self.total_count = len(tasks)
        self.save()

    def _generate_mixed_fraction_tasks(self):
        """Генерация заданий для урока 1: смешанные и неправильные дроби"""
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
        
        return tasks

    def _generate_comparison_tasks(self):
        """Генерация заданий для урока 2: сравнение и сокращение дробей"""
        tasks = []
        
        # 3 задания на сокращение дробей
        for _ in range(3):
            # Выбираем общий делитель
            gcd_value = random.choice([2, 3, 4, 5, 6])
            # Генерируем несокращённую дробь
            numerator_reduced = random.randint(1, 8)
            denominator_reduced = random.randint(numerator_reduced + 1, 12)
            
            numerator = numerator_reduced * gcd_value
            denominator = denominator_reduced * gcd_value
            
            tasks.append({
                'type': 'reduce',
                'numerator': numerator,
                'denominator': denominator,
                'answer': f"{numerator_reduced}/{denominator_reduced}"
            })

        # 3 задания на сравнение дробей с одинаковым знаменателем
        for _ in range(3):
            denominator = random.randint(5, 15)
            num1 = random.randint(1, denominator - 1)
            num2 = random.randint(1, denominator - 1)
            while num1 == num2:
                num2 = random.randint(1, denominator - 1)
            
            if num1 > num2:
                answer = ">"
            elif num1 < num2:
                answer = "<"
            else:
                answer = "="
            
            tasks.append({
                'type': 'compare_same_denom',
                'numerator1': num1,
                'denominator1': denominator,
                'numerator2': num2,
                'denominator2': denominator,
                'answer': answer
            })

        # 3 задания на сравнение дробей с разными знаменателями
        for _ in range(3):
            # Используем простые знаменатели для простоты
            denominators = [2, 3, 4, 5, 6, 8, 10, 12]
            denom1 = random.choice(denominators)
            denom2 = random.choice([d for d in denominators if d != denom1])
            
            num1 = random.randint(1, denom1 - 1)
            num2 = random.randint(1, denom2 - 1)
            
            # Используем Fraction для точного сравнения
            frac1 = Fraction(num1, denom1)
            frac2 = Fraction(num2, denom2)
            
            if frac1 > frac2:
                answer = ">"
            elif frac1 < frac2:
                answer = "<"
            else:
                answer = "="
            
            tasks.append({
                'type': 'compare_diff_denom',
                'numerator1': num1,
                'denominator1': denom1,
                'numerator2': num2,
                'denominator2': denom2,
                'answer': answer
            })

        # 1 задание повышенной сложности (обязательно для 7)
        # Сокращение дроби с большими числами И сравнение
        gcd_large = random.choice([6, 8, 9, 12, 15])
        num_base = random.randint(3, 10)
        denom_base = random.randint(num_base + 2, 15)
        
        numerator_large = num_base * gcd_large
        denominator_large = denom_base * gcd_large
        
        tasks.append({
            'type': 'reduce_hard',
            'numerator': numerator_large,
            'denominator': denominator_large,
            'answer': f"{num_base}/{denom_base}",
            'difficulty': 'hard',
            'points': 2  # Это задание даёт 2 балла вместо 1
        })
        
        return tasks

    def check_answers(self, submitted_answers):
        """Проверка ответов и выставление оценки"""
        tasks = json.loads(self.tasks_data)
        correct = 0
        total_points = 0
        earned_points = 0
        
        for i, task in enumerate(tasks):
            user_answer = submitted_answers.get(str(i), '').strip()
            correct_answer = task['answer'].strip()
            
            # Получаем количество баллов за задание
            task_points = task.get('points', 1)
            total_points += task_points
            
            # Проверка ответа
            is_correct = False
            
            if task.get('type') in ['compare_same_denom', 'compare_diff_denom']:
                # Для сравнений нормализуем ответ
                user_answer_normalized = user_answer.replace(' ', '')
                correct_answer_normalized = correct_answer.replace(' ', '')
                is_correct = user_answer_normalized == correct_answer_normalized
            else:
                # Для дробей проверяем точное совпадение или эквивалентность
                is_correct = user_answer.lower() == correct_answer.lower()
            
            if is_correct:
                correct += 1
                earned_points += task_points
        
        self.correct_count = correct
        self.answers = json.dumps(submitted_answers, ensure_ascii=False)
        self.submitted_at = timezone.now()

        # Выставление оценки по 7-бальной системе (на основе набранных баллов)
        percentage = (earned_points / total_points) * 100 if total_points > 0 else 0
        
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
