# Generated by Django 2.2.4 on 2020-09-25 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orgs", "0070_populate_plan_start"),
    ]

    operations = [
        migrations.AddField(
            model_name="orgactivity", name="plan_active_contact_count", field=models.IntegerField(null=True),
        ),
    ]
