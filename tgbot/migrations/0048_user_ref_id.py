# Generated by Django 3.2.13 on 2022-06-04 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0047_user_merchant_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='ref_id',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
