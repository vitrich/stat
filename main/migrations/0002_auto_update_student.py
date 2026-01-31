# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        # Удаляем старые поля
        migrations.RemoveField(
            model_name='student',
            name='is_registered',
        ),
        migrations.RemoveField(
            model_name='student',
            name='parent_contact',
        ),
        # Добавляем новое поле
        migrations.AddField(
            model_name='student',
            name='class_name',
            field=models.CharField(max_length=50, blank=True, null=True, verbose_name='Класс'),
        ),
        # Изменяем full_name - убираем unique
        migrations.AlterField(
            model_name='student',
            name='full_name',
            field=models.CharField(max_length=200, verbose_name='ФИО'),
        ),
    ]
