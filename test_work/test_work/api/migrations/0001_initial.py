# Generated by Django 2.2.16 on 2022-02-06 11:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('code', models.CharField(max_length=10)),
                ('tag', models.CharField(max_length=50, null=True)),
                ('time_zone', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Mailing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_send_time', models.DateTimeField()),
                ('text', models.TextField()),
                ('tags', models.CharField(max_length=50)),
                ('filters', models.CharField(max_length=50)),
                ('end_send_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.IntegerField(unique=True)),
                ('send_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('S', 'send'), ('N', 'not send')], max_length=1)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='api.Contact')),
                ('mailing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='api.Mailing')),
            ],
        ),
    ]
