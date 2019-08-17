# Generated by Django 2.2.4 on 2019-08-15 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0004_auto_20190815_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='duration',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='game',
            name='last_accessed',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
