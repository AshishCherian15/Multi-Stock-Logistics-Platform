# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0005_storageunit_updated_at_storageunit_updated_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='storagebooking',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('refunded', 'Refunded')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='storagebooking',
            name='payment_method',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='storagebooking',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('active', 'Active'), ('expired', 'Expired'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
    ]
