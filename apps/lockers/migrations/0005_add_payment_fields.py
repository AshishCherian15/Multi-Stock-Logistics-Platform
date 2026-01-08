# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lockers', '0004_locker_created_by_locker_updated_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='lockerbooking',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('refunded', 'Refunded')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='lockerbooking',
            name='payment_method',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
