# Generated by Django 3.2.12 on 2022-04-15 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0032_auto_20220412_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='terms',
            name='size_fee',
            field=models.FloatField(default=0),
        ),
    ]
