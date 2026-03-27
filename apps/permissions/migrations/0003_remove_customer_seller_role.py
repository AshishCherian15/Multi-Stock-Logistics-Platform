# Generated migration to remove customer_seller role

from django.db import migrations, models

def migrate_customer_seller_to_customer(apps, schema_editor):
    """Convert all customer_seller users to customer role"""
    UserRole = apps.get_model('permissions', 'UserRole')
    UserRole.objects.filter(role='customer_seller').update(role='customer')

def reverse_migration(apps, schema_editor):
    """Reverse migration - no action needed"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0002_alter_userrole_role'),
    ]

    operations = [
        migrations.RunPython(migrate_customer_seller_to_customer, reverse_migration),
        migrations.AlterField(
            model_name='userrole',
            name='role',
            field=models.CharField(
                choices=[
                    ('superadmin', 'SuperAdmin'),
                    ('admin', 'Admin (Partner)'),
                    ('subadmin', 'SubAdmin (Manager)'),
                    ('supervisor', 'Supervisor (SeniorStaff)'),
                    ('staff', 'Staff (Employee)'),
                    ('customer', 'Customer'),
                    ('guest', 'Guest')
                ],
                default='customer',
                max_length=20
            ),
        ),
    ]
