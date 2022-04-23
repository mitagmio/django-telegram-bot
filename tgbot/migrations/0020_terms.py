# Generated by Django 3.2.12 on 2022-04-09 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0019_user_merchant_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Terms',
            fields=[
                ('id', models.PositiveBigIntegerField(primary_key=True, serialize=False)),
                ('terms_of_use_user', models.TextField(blank=True, null=True)),
                ('terms_of_use_merchant', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
