# Generated by Django 3.2.13 on 2022-06-02 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0042_order_transfer'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='merchant_delivery',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='transfer',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='transfer',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
