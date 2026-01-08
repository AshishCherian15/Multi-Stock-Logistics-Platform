from django.db import migrations


def add_missing_orderitem_columns(apps, schema_editor):
    connection = schema_editor.connection
    cursor = connection.cursor()

    def has_column(table_name, column_name):
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        return any(row[1] == column_name for row in cursor.fetchall())

    table = 'orders_orderitem'

    if not has_column(table, 'product_name'):
        cursor.execute(
            "ALTER TABLE orders_orderitem ADD COLUMN product_name varchar(200) NOT NULL DEFAULT ''"
        )

    if not has_column(table, 'seller'):
        cursor.execute(
            "ALTER TABLE orders_orderitem ADD COLUMN seller varchar(200) NULL DEFAULT ''"
        )


def noop_reverse(apps, schema_editor):
    # No-op: we don't drop columns on reverse to avoid data loss
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_assigned_to_order_customer_user_and_more'),
    ]

    operations = [
        migrations.RunPython(add_missing_orderitem_columns, noop_reverse),
    ]
