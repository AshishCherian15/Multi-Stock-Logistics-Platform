from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('orders','0006_alter_order_status'),('auth','0012_alter_user_first_name_max_length')]
    operations = [
        migrations.CreateModel(
            name='ReturnRequest',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('reason',models.CharField(choices=[('defective','Defective'),('wrong_item','Wrong Item'),('not_as_described','Not as Described'),('damaged_in_transit','Damaged in Transit'),('other','Other')],max_length=30)),
                ('description',models.TextField()),
                ('status',models.CharField(choices=[('pending','Pending'),('approved','Approved'),('rejected','Rejected'),('completed','Completed')],default='pending',max_length=20)),
                ('refund_amount',models.DecimalField(decimal_places=2,default=0,max_digits=10)),
                ('created_at',models.DateTimeField(auto_now_add=True)),
                ('updated_at',models.DateTimeField(auto_now=True)),
                ('order',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='return_requests',to='orders.order')),
                ('customer',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='auth.user')),
                ('handled_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='handled_returns',to='auth.user')),
            ],
            options={'ordering':['-created_at']},
        ),
    ]
