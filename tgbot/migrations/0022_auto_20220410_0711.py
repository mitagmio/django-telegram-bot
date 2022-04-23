# Generated by Django 3.2.12 on 2022-04-10 07:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0021_auto_20220410_0628'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_fee',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(blank=True, max_length=32, null=True)),
                ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_id_suggestion_set', to='tgbot.order')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
    ]