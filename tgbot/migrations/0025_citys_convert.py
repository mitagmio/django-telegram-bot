# Generated by Django 3.2.12 on 2022-04-10 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0024_rename_date_time_order_date_time_execut'),
    ]

    operations = [
        migrations.AddField(
            model_name='citys',
            name='convert',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
