from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import quotations.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quotation_number', models.CharField(editable=False, max_length=30, unique=True)),
                ('customer_name', models.CharField(max_length=200)),
                ('customer_email', models.EmailField(max_length=254)),
                ('customer_phone', models.CharField(blank=True, max_length=30)),
                ('customer_company', models.CharField(blank=True, max_length=200)),
                ('notes', models.TextField(blank=True)),
                ('terms', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('sent', 'Sent'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('expired', 'Expired'), ('converted', 'Converted to Order')], default='draft', max_length=20)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('tax_rate', models.DecimalField(decimal_places=2, default=0, help_text='Tax percentage, e.g. 10 for 10%', max_digits=5)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('valid_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('expires_at', models.DateTimeField(default=quotations.models.default_expiry)),
                ('converted_order_id', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quotations', to='auth.user')),
            ],
            options={
                'db_table': 'quotations',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['status'], name='quotations_status_idx'),
                    models.Index(fields=['expires_at'], name='quotations_expires_idx'),
                    models.Index(fields=['customer_email'], name='quotations_email_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='QuotationItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=500)),
                ('quantity', models.DecimalField(decimal_places=3, default=1, max_digits=12)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('discount_pct', models.DecimalField(decimal_places=2, default=0, help_text='Line-level discount percentage', max_digits=5)),
                ('quotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='quotations.quotation')),
            ],
            options={
                'db_table': 'quotation_items',
            },
        ),
    ]
