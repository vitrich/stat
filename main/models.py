from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

import json
import random
import math
from fractions import Fraction


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacherprofile')
    fullname = models.CharField(max_length=200, verbose_name="ФИО")
    email = models.EmailField(blank=True, null=True)

    class Meta:
        verbose_name = "Учитель"
        verbose_name_plural = "Учителя"

    def __str__(self):
        return self.fullname


class Group(models.Model):
    GROUP_CHOICES = (
        (1, "1"),
        (2, "2"),
        (2.1, "2.1"),
        (2.2, "2.2"),
        (3, "3"),
    )

    number = models.FloatField(choices=GROUP_CHOICES, unique=True, verbose_name="Номер группы")
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='groups', verbose_name="Учитель")
    description = models.TextField(blank=True, verbose_name="Описание")
    color = models.CharField(max_length=7, default="#bd2e8d", verbose_name="Цвет")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
        ordering = ["number"]

    def __str__(self):
        return f"{self.number}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    fullname = models.CharField(max_length=200, verbose_name="ФИО")
    classname = models.CharField(max_length=50, blank=True, null=True, verbose_name="Класс")
    currentgroup = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Группа")

    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"
        ordering = ["fullname"]

    def __str__(self):
        return self.fullname


class GroupHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grouphistory', verbose_name="Ученик")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Группа")
    transferdate = models.DateField(verbose_name="Дата перевода")
    reason = models.TextField(blank=True, verbose_name="Причина")

    class Meta:
        verbose_name = "История групп"
        verbose_name_plural = "История групп"
        ordering = ["-transferdate"]

    def __str__(self):
        return f"{self.student.fullname} → {self.group.number} ({self.transferdate})"


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    date = models.DateField(verbose_name="Дата")
    subject = models.CharField(max_length=100, default="", verbose_name="Предмет")
    grade = models.CharField(max_length=20, default="5", verbose_name="Класс")
    theorycontent = models.TextField(verbose_name="Теория (HTML)")
    durationminutes = models.IntegerField(default=40, verbose_name="Длительность урока (мин)")
    testdurationminutes = models.IntegerField(default=5, verbose_name="Длительность теста (мин)")
    isactive = models.BooleanField(default=True, verbose_name="Активен")
    createdat = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.title} ({self.date})"


class LessonTask(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='tasks')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='lessontasks')

    tasksdata = models.TextField(verbose_name="Задания (JSON)")
    answers = models.TextField(blank=True, null=True, verbose_name="Ответы ученика (JSON)")

    score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(7)], verbose_name="Оценка (0-7)")
    correctcount = models.IntegerField(default=0, verbose_name="Верно")
    totalcount = models.IntegerField(default=10, verbose_name="Всего")
    submittedat = models.DateTimeField(null=True, blank=True, verbose_name="Время сдачи")

    class Meta:
        verbose_name = "Задания урока"
        verbose_name_plural = "Задания уроков"
        unique_together = ('lesson', 'student')

    def __str__(self):
        return f"{self.student.fullname} - {self.lesson.title}"

    def generate_tasks(self):
        lesson_date_str = str(self.lesson.date)
        title = (self.lesson.title or "").lower()

        # Урок 2: сравнение/сокращение
        if lesson_date_str == "2026-02-03" or ("сравнен" in title) or ("сокращен" in title):
            tasks = self.generate_comparison_tasks()

        # Урок 3: общий знаменатель + сложение/вычитание
        elif lesson_date_str == "2026-02-09":
            tasks = self.generate_common_denom_add_sub_tasks()

        # Остальные: смешанные дроби
        else:
            tasks = self.generate_mixed_fraction_tasks()

        self.tasksdata = json.dumps(tasks, ensure_ascii=False)
        self.totalcount = len(tasks)
        self.save()

    def generate_mixed_fraction_tasks(self):
        tasks = []

        # 1) Определить вид дроби (правильная/неправильная)
        for _ in range(3):
            numerator = random.randint(1, 20)
            denominator = random.randint(2, 15)
            tasks.append({
                "type": "classify",
                "numerator": numerator,
                "denominator": denominator,
                "answer": "proper" if numerator < denominator else "improper",
                "points": 1
            })

        # 2) Смешанное число -> неправильная дробь
        for _ in range(3):
            whole = random.randint(1, 10)
            numerator = random.randint(1, 8)
            denominator = random.randint(2, 9)
            ans_num = whole * denominator + numerator
            tasks.append({
                "type": "mixedtoimproper",
                "whole": whole,
                "numerator": numerator,
                "denominator": denominator,
                "answer": f"{ans_num}/{denominator}",
                "points": 1
            })

        # 3) Неправильная дробь -> смешанное число
        for _ in range(4):
            denominator = random.randint(2, 9)
            whole = random.randint(1, 8)
            numerator = random.randint(1, denominator - 1)
            improper_num = whole * denominator + numerator
            tasks.append({
                "type": "impropertomixed",
                "numerator": improper_num,
                "denominator": denominator,
                "answer": f"{whole} {numerator}/{denominator}",
                "points": 1
            })

        return tasks

    def generate_comparison_tasks(self):
        tasks = []

        # 1) Сократить дробь
        for _ in range(3):
            gcd_value = random.choice([2, 3, 4, 5, 6])
            numerator_reduced = random.randint(1, 8)
            denominator_reduced = random.randint(numerator_reduced + 1, 12)
            numerator = numerator_reduced * gcd_value
            denominator = denominator_reduced * gcd_value
            tasks.append({
                "type": "reduce",
                "numerator": numerator,
                "denominator": denominator,
                "answer": f"{numerator_reduced}/{denominator_reduced}",
                "points": 1
            })

        # 2) Сравнить дроби с одинаковым знаменателем
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
                "type": "comparesamedenom",
                "numerator1": num1, "denominator1": denominator,
                "numerator2": num2, "denominator2": denominator,
                "answer": answer,
                "points": 1
            })

        # 3) Сравнить дроби с разными знаменателями
        denominators = [2, 3, 4, 5, 6, 8, 10, 12]
        for _ in range(3):
            denom1 = random.choice(denominators)
            denom2 = random.choice([d for d in denominators if d != denom1])
            num1 = random.randint(1, denom1 - 1)
            num2 = random.randint(1, denom2 - 1)
            frac1 = Fraction(num1, denom1)
            frac2 = Fraction(num2, denom2)
            if frac1 > frac2:
                answer = ">"
            elif frac1 < frac2:
                answer = "<"
            else:
                answer = "="
            tasks.append({
                "type": "comparediffdenom",
                "numerator1": num1, "denominator1": denom1,
                "numerator2": num2, "denominator2": denom2,
                "answer": answer,
                "points": 1
            })

        # 4) “Сложное” сокращение (как было)
        gcd_large = random.choice([6, 8, 9, 12, 15])
        num_base = random.randint(3, 10)
        denom_base = random.randint(num_base + 2, 15)
        numerator_large = num_base * gcd_large
        denominator_large = denom_base * gcd_large
        tasks.append({
            "type": "reducehard",
            "numerator": numerator_large,
            "denominator": denominator_large,
            "answer": f"{num_base}/{denom_base}",
            "difficulty": "hard",
            "points": 2
        })

        return tasks

    # ---------- Урок 3 ----------

    def generate_common_denom_add_sub_tasks(self):
        tasks = []
        denominators = [2, 3, 4, 5, 6, 8, 10, 12]

        def lcm(a, b):
            return abs(a * b) // math.gcd(a, b)

        # 1–3: привести к общему знаменателю
        for _ in range(3):
            b = random.choice(denominators)
            d = random.choice([x for x in denominators if x != b])
            a = random.randint(1, b - 1)
            c = random.randint(1, d - 1)

            L = lcm(b, d)
            k1 = L // b
            k2 = L // d

            tasks.append({
                "type": "common_denom",
                "numerator1": a, "denominator1": b,
                "numerator2": c, "denominator2": d,
                "common_den": L,
                "answer": f"{a*k1}/{L}, {c*k2}/{L}",
                "points": 1
            })

        # 4–6: сложение
        for _ in range(3):
            b = random.choice(denominators)
            d = random.choice([x for x in denominators if x != b])
            a = random.randint(1, b - 1)
            c = random.randint(1, d - 1)

            res = Fraction(a, b) + Fraction(c, d)
            tasks.append({
                "type": "add_diff",
                "numerator1": a, "denominator1": b,
                "numerator2": c, "denominator2": d,
                "answer": f"{res.numerator}/{res.denominator}",
                "points": 1
            })

        # 7–9: вычитание (положительный результат)
        for _ in range(3):
            b = random.choice(denominators)
            d = random.choice([x for x in denominators if x != b])
            a = random.randint(1, b - 1)
            c = random.randint(1, d - 1)

            f1 = Fraction(a, b)
            f2 = Fraction(c, d)
            if f1 < f2:
                a, b, c, d = c, d, a, b
                f1, f2 = f2, f1

            res = f1 - f2
            tasks.append({
                "type": "sub_diff",
                "numerator1": a, "denominator1": b,
                "numerator2": c, "denominator2": d,
                "answer": f"{res.numerator}/{res.denominator}",
                "points": 1
            })

        return tasks

    def _normalize_fraction(self, s: str):
        s = (s or "").strip().replace(" ", "")
        if "/" not in s:
            return None
        try:
            p, q = s.split("/", 1)
            return Fraction(int(p), int(q))
        except Exception:
            return None

    # ---------- Проверка ----------

    def check_answers(self, submitted_answers):
        tasks = json.loads(self.tasksdata)
        correct = 0
        total_points = 0
        earned_points = 0

        for i, task in enumerate(tasks):
            useranswer = (submitted_answers.get(str(i), "") or "").strip()
            correctanswer = (task.get("answer", "") or "").strip()

            task_points = task.get("points", 1)
            total_points += task_points

            task_type = task.get("type")
            is_correct = False

            if task_type in ("add_diff", "sub_diff"):
                ua = self._normalize_fraction(useranswer)
                ca = self._normalize_fraction(correctanswer)
                is_correct = (ua is not None and ca is not None and ua == ca)

            elif task_type == "common_denom":
                parts_u = [p.strip() for p in (useranswer or "").split(",")]
                parts_c = [p.strip() for p in (correctanswer or "").split(",")]
                if len(parts_u) == 2 and len(parts_c) == 2:
                    u1 = self._normalize_fraction(parts_u[0])
                    u2 = self._normalize_fraction(parts_u[1])
                    c1 = self._normalize_fraction(parts_c[0])
                    c2 = self._normalize_fraction(parts_c[1])
                    is_correct = (u1 == c1 and u2 == c2)
                else:
                    is_correct = False

            elif task_type in ("comparesamedenom", "comparediffdenom"):
                useranswer_normalized = (useranswer or "").replace(" ", "")
                correctanswer_normalized = (correctanswer or "").replace(" ", "")
                is_correct = (useranswer_normalized == correctanswer_normalized)

            else:
                is_correct = (str(useranswer).strip().lower() == str(correctanswer).strip().lower())

            if is_correct:
                correct += 1
                earned_points += task_points

        self.correctcount = correct
        self.answers = json.dumps(submitted_answers, ensure_ascii=False)
        self.submittedat = timezone.now()

        percentage = (earned_points / total_points * 100) if total_points > 0 else 0

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


class Assignment(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='assignments', verbose_name="Группа")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assignments', verbose_name="Учитель")
    deadline = models.DateTimeField(verbose_name="Дедлайн")
    createdat = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Задание"
        verbose_name_plural = "Задания"
        ordering = ["-createdat"]

    def __str__(self):
        return f"{self.title} ({self.group.number})"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions', verbose_name="Задание")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions', verbose_name="Ученик")
    answertext = models.TextField(blank=True, verbose_name="Ответ")
    file = models.FileField(upload_to="submissions/", blank=True, null=True, verbose_name="Файл")
    submittedat = models.DateTimeField(auto_now_add=True, verbose_name="Сдано")
    grade = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(7)], verbose_name="Оценка (0-7)")
    teachercomment = models.TextField(blank=True, verbose_name="Комментарий учителя")

    class Meta:
        verbose_name = "Сдача"
        verbose_name_plural = "Сдачи"
        unique_together = ("assignment", "student")
        ordering = ["-submittedat"]

    def __str__(self):
        return f"{self.student.fullname} - {self.assignment.title}"
