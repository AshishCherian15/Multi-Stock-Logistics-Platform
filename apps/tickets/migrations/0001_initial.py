from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('auth','0012_alter_user_first_name_max_length')]
    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('ticket_number',models.CharField(editable=False,max_length=20,unique=True)),
                ('subject',models.CharField(max_length=200)),
                ('description',models.TextField()),
                ('category',models.CharField(choices=[('order','Order Issue'),('payment','Payment Issue'),('rental','Rental Issue'),('storage','Storage Issue'),('locker','Locker Issue'),('account','Account Issue'),('other','Other')],default='other',max_length=20)),
                ('status',models.CharField(choices=[('open','Open'),('in_progress','In Progress'),('resolved','Resolved'),('closed','Closed')],default='open',max_length=20)),
                ('priority',models.CharField(choices=[('low','Low'),('medium','Medium'),('high','High'),('urgent','Urgent')],default='medium',max_length=20)),
                ('created_at',models.DateTimeField(auto_now_add=True)),
                ('updated_at',models.DateTimeField(auto_now=True)),
                ('resolved_at',models.DateTimeField(blank=True,null=True)),
                ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='tickets',to='auth.user')),
                ('assigned_to',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='assigned_tickets',to='auth.user')),
            ],
            options={'ordering':['-created_at']},
        ),
        migrations.CreateModel(
            name='TicketMessage',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('message',models.TextField()),
                ('is_staff_reply',models.BooleanField(default=False)),
                ('attachment',models.FileField(blank=True,null=True,upload_to='ticket_attachments/')),
                ('created_at',models.DateTimeField(auto_now_add=True)),
                ('ticket',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='messages',to='tickets.ticket')),
                ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='auth.user')),
            ],
            options={'ordering':['created_at']},
        ),
    ]
