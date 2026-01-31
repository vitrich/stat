import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import Student, Group, GroupHistory
from datetime import date

# Читаем данные из файла
df = pd.read_csv('student_groups_history.csv')


def shorten_name(full_name):
    """Преобразует полное ФИО в короткое (Фамилия Имя)"""
    if pd.isna(full_name):
        return None
    parts = str(full_name).strip().split()
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1]}"
    return str(full_name)


print("=" * 80)
print("ПРОВЕРКА РАСХОЖДЕНИЙ И ОБНОВЛЕНИЕ ИСТОРИИ")
print("=" * 80)

# Даты
dates_map = {
    'september': date(2025, 9, 1),
    'q2_start': date(2025, 11, 1),  # Примерная дата начала 2 четверти
    'december': date(2025, 12, 16),
    'january': date(2026, 1, 12)
}

groups = {g.number: g for g in Group.objects.all()}

# 1. Обновляем классы учеников
print("\n📚 Обновление классов учеников:")
for idx, row in df.iterrows():
    name = row['name']
    class_name = row['class']

    try:
        student = Student.objects.get(full_name=name)
        if student.class_name != class_name:
            old_class = student.class_name or 'не указан'
            student.class_name = class_name
            student.save()
            print(f"  ✓ {name}: класс обновлен ({old_class} → {class_name})")
    except Student.DoesNotExist:
        print(f"  ⚠️ Ученик не найден: {name}")

# 2. Собираем всю историю из файла
file_history = {}
for idx, row in df.iterrows():
    name = row['name']
    file_history[name] = {
        'september': row['september'],
        'q2_start': row['q2_start'],
        'december': row['december'],
        'january': row['january']
    }

# 3. Получаем текущую историю из БД
print("\n📊 Сравнение с историей в БД:")
db_history = {}
for entry in GroupHistory.objects.all().select_related('student', 'group').order_by('student_id', 'transfer_date'):
    student_name = entry.student.full_name
    if student_name not in db_history:
        db_history[student_name] = {}

    # Определяем к какой дате относится
    if entry.transfer_date == date(2025, 9, 1):
        db_history[student_name]['september'] = entry.group.number
    elif entry.transfer_date == date(2025, 11, 1):
        db_history[student_name]['q2_start'] = entry.group.number
    elif entry.transfer_date == date(2025, 12, 16):
        db_history[student_name]['december'] = entry.group.number
    elif entry.transfer_date == date(2026, 1, 12):
        db_history[student_name]['january'] = entry.group.number

# 4. Находим расхождения
discrepancies = []
for name, file_data in file_history.items():
    db_data = db_history.get(name, {})

    for period in ['september', 'q2_start', 'december', 'january']:
        file_group = file_data.get(period)
        db_group = db_data.get(period)

        # Пропускаем если в файле 0 или NaN
        if pd.isna(file_group) or file_group == 0:
            continue

        if file_group != db_group:
            discrepancies.append({
                'name': name,
                'period': period,
                'file_group': file_group,
                'db_group': db_group
            })
            print(f"  🔍 {name} ({period}): файл={file_group}, БД={db_group}")

print(f"\n{'=' * 80}")
print(f"Найдено расхождений: {len(discrepancies)}")
print(f"{'=' * 80}")

# 5. Предлагаем обновить
if discrepancies:
    response = input("\n❓ Обновить историю на основе файла? (yes/no): ")
    if response.lower() == 'yes':
        print("\n🔄 Обновление истории...")

        # Очищаем историю
        GroupHistory.objects.all().delete()
        print("  ✓ История очищена")

        # Добавляем новую историю из файла
        added_count = 0
        for idx, row in df.iterrows():
            name = row['name']

            try:
                student = Student.objects.get(full_name=name)

                # Добавляем записи для каждой даты
                for period, date_val in dates_map.items():
                    group_num = row[period]

                    # Пропускаем если 0 или NaN
                    if pd.isna(group_num) or group_num == 0:
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

                # Обновляем текущую группу
                jan_group = row['january']
                if not pd.isna(jan_group) and jan_group in groups:
                    student.current_group = groups[jan_group]
                    student.save()

            except Student.DoesNotExist:
                print(f"  ⚠️ Ученик не найден: {name}")

        print(f"  ✓ Добавлено записей: {added_count}")
        print("\n✅ История успешно обновлена!")
    else:
        print("\n❌ Обновление отменено")
else:
    print("\n✅ Расхождений не найдено!")
