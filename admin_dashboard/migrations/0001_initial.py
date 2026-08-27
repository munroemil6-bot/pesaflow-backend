# Generated manually for the initial admin dashboard support schema.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="DashboardSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=100, unique=True)),
                ("data", models.JSONField()),
                ("generated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("-generated_at",)},
        ),
        migrations.CreateModel(
            name="DashboardLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=100)),
                ("details", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("admin", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="dashboard_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.AddIndex(model_name="dashboardlog", index=models.Index(fields=("action", "created_at"), name="admin_dashb_action_89d47e_idx")),
    ]
