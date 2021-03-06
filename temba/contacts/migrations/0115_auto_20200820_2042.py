# Generated by Django 2.2.10 on 2020-08-20 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contacts", "0114_populate_contact_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contact",
            name="status",
            field=models.CharField(
                choices=[("A", "Active"), ("B", "Blocked"), ("S", "Stopped"), ("V", "Archived")],
                default="A",
                max_length=1,
            ),
        ),
    ]
