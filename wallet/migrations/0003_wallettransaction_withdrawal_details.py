from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0002_wallettransaction_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallettransaction',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='wallettransaction',
            name='provider_reference',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]