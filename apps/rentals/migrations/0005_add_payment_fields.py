# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0004_rentalitem_updated_at_rentalitem_updated_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='rentalbooking',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('refunded', 'Refunded')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='rentalbooking',
            name='payment_method',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='rentalbooking',
            name='delivery_option',
            field=models.CharField(choices=[('pickup', 'Pickup'), ('delivery', 'Delivery')], default='pickup', max_length=20),
        ),
    ]
