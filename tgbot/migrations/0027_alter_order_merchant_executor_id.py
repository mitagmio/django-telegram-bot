# Generated by Django 3.2.12 on 2022-04-10 09:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0026_auto_20220410_0820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='merchant_executor_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='merchant_executor_id_order_set', to='tgbot.user'),
        ),
    ]
