from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_remove_student_is_registered_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="grouphistory",
            old_name="transfer_date",
            new_name="transferdate",
        ),
    ]
