# Generated by Django 3.2.13 on 2022-06-02 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0046_remove_user_merchant_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='merchant_delivery',
            field=models.CharField(default='\U0001f6fb Доставка: Самовывозом', max_length=256),
        ),
    ]