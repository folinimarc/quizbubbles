# Generated by Django 2.2.4 on 2019-08-25 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bubble',
            name='password',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='username',
            field=models.CharField(max_length=20),
        ),
    ]