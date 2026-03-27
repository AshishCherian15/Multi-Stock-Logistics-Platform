from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('goods','0005_listmodel_created_by'),('warehouse','0002_listmodel_warehouse_image'),('auth','0012_alter_user_first_name_max_length')]
    operations = [
        migrations.CreateModel(
            name='StockTransfer',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('quantity',models.IntegerField()),
                ('status',models.CharField(choices=[('pending','Pending'),('in_transit','In Transit'),('completed','Completed'),('cancelled','Cancelled')],default='pending',max_length=20)),
                ('notes',models.TextField(blank=True)),
                ('created_at',models.DateTimeField(auto_now_add=True)),
                ('updated_at',models.DateTimeField(auto_now=True)),
                ('product',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='goods.listmodel')),
                ('from_warehouse',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='outgoing_transfers',to='warehouse.listmodel')),
                ('to_warehouse',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='incoming_transfers',to='warehouse.listmodel')),
                ('created_by',models.ForeignKey(null=True,on_delete=django.db.models.deletion.SET_NULL,to='auth.user')),
            ],
            options={'ordering':['-created_at']},
        ),
    ]
