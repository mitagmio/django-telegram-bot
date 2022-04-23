# Generated by Django 3.2.12 on 2022-04-06 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0003_rm_unused_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='P2p',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('timestamp', models.PositiveBigIntegerField(primary_key=True, serialize=False)),
                ('date_time', models.DateTimeField()),
                ('usdt_lkr', models.FloatField()),
                ('uah_usdt', models.FloatField()),
                ('eur_revolut_usdt', models.FloatField()),
                ('rub_tinkoff_usdt', models.FloatField()),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
    ]
