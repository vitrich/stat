import os
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import Student, Group, GroupHistory
from datetime import date

print("=" * 80)
print("ДОБАВЛЕНИЕ ИСТОРИИ С ДАТОЙ 15.10.2025")
print("=" * 80)

# Все даты включая новую
dates_map = {
    'september': date(2025, 9, 1),
    'october_15': date(2025, 10, 15),  # НОВАЯ ДАТА!
    'december': date(2025, 12, 16),
    'january': date(2026, 1, 12)
}

# Читаем CSV файл
file_history = {}
with open('student_groups_with_october.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['name']
        file_history[name] = {
            'class': row['class'],
            'september': float(row['september']) if row['september'] and row['september'] != '0.0' else None,
            'october_15': float(row['october_15']) if row['october_15'] and row['october_15'] != '0.0' else None,
            'december': float(row['december']) if row['december'] and row['december'] != '0.0' else None,
            'january': float(row['january']) if row['january'] and row['january'] != '0.0' else None,
        }

groups = {g.number: g for g in Group.objects.all()}

# Показываем что будем добавлять
print("\n📊 Данные для добавления:")
print(f"Всего учеников: {len(file_history)}")
print(f"Даты: {list(dates_map.keys())}")

# Подсчитываем сколько записей будет добавлено
total_records = 0
for name, file_data in file_history.items():
    for period in ['september', 'october_15', 'december', 'january']:
        if file_data.get(period) is not None:
            total_records += 1

print(f"Всего записей для добавления: {total_records}")

# Спрашиваем подтверждение
response = input("\n❓ Очистить текущую историю и добавить новую? (yes/no): ")

if response.lower() == 'yes':
    print("\n🔄 Обновление истории...")

    # Очищаем историю
    deleted = GroupHistory.objects.all().delete()
    print(f"  ✓ Удалено старых записей: {deleted[0]}")

    # Добавляем новую историю из файла
    added_count = 0
    errors = []

    for name, file_data in file_history.items():
        try:
            student = Student.objects.get(full_name=name)

            # Обновляем класс
            if file_data['class'] and student.class_name != file_data['class']:
                student.class_name = file_data['class']
                student.save()

            # Добавляем записи для каждой даты
            for period, date_val in dates_map.items():
                group_num = file_data.get(period)

                if group_num is None:
                    continue

                if group_num in groups:
                    group = groups[group_num]

                    GroupHistory.objects.create(
                        student=student,
                        group=group,
                        transfer_date=date_val,
                        reason=f'Данные из файла ({period})'
                    )
                    added_count += 1
                else:
                    errors.append(f"Группа {group_num} не найдена для {name}")

            # Обновляем текущую группу
            jan_group = file_data.get('january')
            if jan_group and jan_group in groups:
                student.current_group = groups[jan_group]
                student.save()

        except Student.DoesNotExist:
            errors.append(f"Ученик не найден: {name}")
        except Student.MultipleObjectsReturned:
            errors.append(f"Несколько учеников с именем: {name}")

    print(f"  ✓ Добавлено записей: {added_count}")

    if errors:
        print(f"\n⚠️ Ошибки ({len(errors)}):")
        for error in errors[:10]:  # Показываем первые 10
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... и ещё {len(errors) - 10}")

    print("\n✅ История успешно обновлена с датой 15.10.2025!")
else:
    print("\n❌ Обновление отменено")
