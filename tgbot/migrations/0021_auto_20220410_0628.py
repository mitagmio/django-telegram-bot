# Generated by Django 3.2.12 on 2022-04-10 06:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0020_terms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='citys',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='location',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='pairs',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='periods',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='terms',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('city', models.CharField(blank=True, max_length=32, null=True)),
                ('pair', models.CharField(blank=True, max_length=32, null=True)),
                ('summ', models.FloatField(default=0)),
                ('period', models.CharField(blank=True, max_length=32, null=True)),
                ('timestamp_execut', models.PositiveBigIntegerField()),
                ('date_time', models.DateTimeField()),
                ('client_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_id_order_set', to='tgbot.user')),
                ('merchant_executor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='merchant_executor_id_order_set', to='tgbot.user')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
    ]