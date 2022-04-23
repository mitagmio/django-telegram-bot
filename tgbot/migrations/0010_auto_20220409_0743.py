# Generated by Django 3.2.12 on 2022-04-09 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0009_citis'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='citi',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='pair',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='summ',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='type_pair',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
