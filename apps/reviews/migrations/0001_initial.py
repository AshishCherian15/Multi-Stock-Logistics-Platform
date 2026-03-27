from django.db import migrations, models
import django.core.validators
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('goods','0005_listmodel_created_by'),('auth','0012_alter_user_first_name_max_length')]
    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('rating',models.IntegerField(validators=[django.core.validators.MinValueValidator(1),django.core.validators.MaxValueValidator(5)])),
                ('title',models.CharField(blank=True,max_length=100)),
                ('body',models.TextField()),
                ('is_verified_purchase',models.BooleanField(default=False)),
                ('created_at',models.DateTimeField(auto_now_add=True)),
                ('updated_at',models.DateTimeField(auto_now=True)),
                ('product',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='reviews',to='goods.listmodel')),
                ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='auth.user')),
            ],
            options={'ordering':['-created_at'],'unique_together':{('product','user')}},
        ),
    ]
