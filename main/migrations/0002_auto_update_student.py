# Generated migration for lesson system

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        # Сначала разрешаем NULL для user в Student
        migrations.AlterField(
            model_name='student',
            name='user',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='auth.user'
            ),
        ),

        # Создаем модель Lesson
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название урока')),
                ('date', models.DateField(verbose_name='Дата урока')),
                ('subject', models.CharField(default='Математика', max_length=100, verbose_name='Предмет')),
                ('grade', models.CharField(default='5', max_length=20, verbose_name='Класс')),
                ('theory_content', models.TextField(verbose_name='Теоретический материал (HTML)')),
                ('duration_minutes', models.IntegerField(default=40, verbose_name='Длительность урока (минут)')),
                ('test_duration_minutes', models.IntegerField(default=5, verbose_name='Время на тест (минут)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Урок',
                'verbose_name_plural': 'Уроки',
                'ordering': ['-date'],
            },
        ),

        # Создаем модель LessonTask
        migrations.CreateModel(
            name='LessonTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tasks_data', models.TextField(verbose_name='Данные заданий (JSON)')),
                ('answers', models.TextField(blank=True, null=True, verbose_name='Ответы ученика (JSON)')),
                ('score', models.IntegerField(
                    blank=True,
                    null=True,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(7)
                    ],
                    verbose_name='Оценка (0-7)'
                )),
                ('correct_count', models.IntegerField(default=0, verbose_name='Правильных ответов')),
                ('total_count', models.IntegerField(default=10, verbose_name='Всего заданий')),
                ('submitted_at', models.DateTimeField(blank=True, null=True, verbose_name='Время сдачи')),
                ('lesson', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tasks',
                    to='main.lesson'
                )),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='lesson_tasks',
                    to='main.student'
                )),
            ],
            options={
                'verbose_name': 'Задание урока',
                'verbose_name_plural': 'Задания уроков',
                'unique_together': {('lesson', 'student')},
            },
        ),
    ]
