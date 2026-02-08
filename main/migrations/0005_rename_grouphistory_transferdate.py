from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("main", "ПРЕДЫДУЩАЯ_МИГРАЦИЯ"),
    ]

    operations = [
        migrations.RenameField(
            model_name="grouphistory",
            old_name="transfer_date",
            new_name="transferdate",
        ),
    ]
