# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_grouphistory'),  # Замените на вашу последнюю миграцию
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='class_name',
            field=models.CharField(max_length=50, blank=True, null=True, verbose_name='Класс'),
        ),
    ]
