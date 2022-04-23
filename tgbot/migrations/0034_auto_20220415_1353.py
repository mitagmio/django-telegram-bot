# Generated by Django 3.2.12 on 2022-04-15 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0033_terms_size_fee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='merchant_client',
            field=models.CharField(default='None', max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='merchant_status',
            field=models.CharField(default='pause', max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='orders_client',
            field=models.CharField(default='None', max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='state',
            field=models.CharField(default='0', max_length=32),
        ),
    ]