# Generated manually for the initial transactions app schema.

import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("fee", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed"), ("cancelled", "Cancelled"), ("refunded", "Refunded")], default="pending", max_length=12)),
                ("reference", models.CharField(default=uuid.uuid4, editable=False, max_length=36, unique=True)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("recipient", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="received_transactions", to=settings.AUTH_USER_MODEL)),
                ("sender", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sent_transactions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="transaction", index=models.Index(fields=["sender", "created_at"], name="transactions_sender__c4b9f4_idx")),
        migrations.AddIndex(model_name="transaction", index=models.Index(fields=["recipient", "created_at"], name="transactions_recipi_eb6fc1_idx")),
        migrations.AddIndex(model_name="transaction", index=models.Index(fields=["status", "created_at"], name="transactions_status_cdf5b5_idx")),
    ]
