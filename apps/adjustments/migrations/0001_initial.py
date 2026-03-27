from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('goods','0005_listmodel_created_by'),('auth','0012_alter_user_first_name_max_length')]
    operations = [
        migrations.CreateModel(
            name='StockAdjustment',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('adjustment_type',models.CharField(choices=[('count','Stock Count'),('correction','Correction'),('damage','Damage Write-off'),('expiry','Expiry Write-off'),('return','Return to Stock')],max_length=20)),
                ('quantity',models.IntegerField()),
                ('reason',models.TextField()),
                ('status',models.CharField(choices=[('pending','Pending'),('approved','Approved'),('rejected','Rejected')],default='pending',max_length=20)),
                ('created_at',models.DateTimeField(auto_now_add=True)),
                ('updated_at',models.DateTimeField(auto_now=True)),
                ('product',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='adjustments',to='goods.listmodel')),
                ('created_by',models.ForeignKey(null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='created_adjustments',to='auth.user')),
                ('approved_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='approved_adjustments',to='auth.user')),
            ],
            options={'ordering':['-created_at']},
        ),
    ]
