from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MpesaPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('merchant_request_id', models.CharField(blank=True, max_length=100)),
                ('checkout_request_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('mpesa_receipt_number', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=10)),
                ('result_code', models.CharField(blank=True, max_length=20)),
                ('result_description', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='mpesa_payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['user', 'status', 'created_at'], name='payments_mpe_user_id_8e1658_idx')],
            },
        ),
    ]