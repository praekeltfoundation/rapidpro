# Generated by Django 2.2.4 on 2020-04-15 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("flows", "0229_auto_20200413_2127")]

    operations = [
        migrations.AddField(
            model_name="flowstart",
            name="start_type",
            field=models.CharField(
                choices=[("M", "Manual"), ("A", "API"), ("F", "Flow Action")], max_length=1, null=True
            ),
        )
    ]
