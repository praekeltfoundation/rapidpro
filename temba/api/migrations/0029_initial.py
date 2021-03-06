# Generated by Django 2.1.8 on 2019-07-01 21:40

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import temba.utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("orgs", "0055_initial"),
        ("contacts", "0102_contacturn_channel"),
        ("auth", "0009_alter_user_last_name_max_length"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="APIToken",
            fields=[
                ("is_active", models.BooleanField(default=True)),
                ("key", models.CharField(max_length=40, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "org",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="api_tokens", to="orgs.Org"
                    ),
                ),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="auth.Group")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="api_tokens",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Resthook",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, help_text="Whether this item is active, use this instead of deleting"
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(
                        blank=True,
                        default=django.utils.timezone.now,
                        editable=False,
                        help_text="When this item was originally created",
                    ),
                ),
                (
                    "modified_on",
                    models.DateTimeField(
                        blank=True,
                        default=django.utils.timezone.now,
                        editable=False,
                        help_text="When this item was last modified",
                    ),
                ),
                ("slug", models.SlugField(help_text="A simple label for this event")),
                (
                    "created_by",
                    models.ForeignKey(
                        help_text="The user which originally created this item",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="api_resthook_creations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "modified_by",
                    models.ForeignKey(
                        help_text="The user which last modified this item",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="api_resthook_modifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "org",
                    models.ForeignKey(
                        help_text="The organization this resthook belongs to",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="resthooks",
                        to="orgs.Org",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ResthookSubscriber",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, help_text="Whether this item is active, use this instead of deleting"
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(
                        blank=True,
                        default=django.utils.timezone.now,
                        editable=False,
                        help_text="When this item was originally created",
                    ),
                ),
                (
                    "modified_on",
                    models.DateTimeField(
                        blank=True,
                        default=django.utils.timezone.now,
                        editable=False,
                        help_text="When this item was last modified",
                    ),
                ),
                ("target_url", models.URLField(help_text="The URL that we will call when our ruleset is reached")),
                (
                    "created_by",
                    models.ForeignKey(
                        help_text="The user which originally created this item",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="api_resthooksubscriber_creations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "modified_by",
                    models.ForeignKey(
                        help_text="The user which last modified this item",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="api_resthooksubscriber_modifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "resthook",
                    models.ForeignKey(
                        help_text="The resthook being subscribed to",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="subscribers",
                        to="api.Resthook",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="WebHookEvent",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", temba.utils.models.JSONAsTextField(default=dict)),
                ("action", models.CharField(default="POST", max_length=8)),
                ("created_on", models.DateTimeField(default=django.utils.timezone.now)),
                ("status", models.CharField(max_length=1, null=True)),
                ("event", models.CharField(max_length=16, null=True)),
                ("try_count", models.IntegerField(null=True)),
                ("org", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="orgs.Org")),
                ("resthook", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="api.Resthook")),
            ],
        ),
        migrations.CreateModel(
            name="WebHookResult",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("url", models.TextField(blank=True, null=True)),
                ("request", models.TextField(blank=True, null=True)),
                ("status_code", models.IntegerField()),
                ("response", models.TextField(blank=True, null=True)),
                ("request_time", models.IntegerField(null=True)),
                ("created_on", models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                (
                    "contact",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="webhook_results",
                        to="contacts.Contact",
                    ),
                ),
                (
                    "org",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="webhook_results", to="orgs.Org"
                    ),
                ),
            ],
        ),
    ]
