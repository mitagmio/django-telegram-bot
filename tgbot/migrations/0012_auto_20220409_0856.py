# Generated by Django 3.2.12 on 2022-04-09 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0011_pairs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pairs',
            name='pair',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='pairs',
            name='ru_pair',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]