# Generated by Django 2.2.4 on 2019-08-14 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gametype', models.IntegerField(choices=[(0, 'Sprint'), (1, 'Marathon')])),
                ('player', models.CharField(max_length=255)),
                ('questions_answered', models.IntegerField()),
                ('question_ids', models.TextField()),
                ('started', models.DateTimeField(auto_now_add=True)),
                ('finished', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('answer_a', models.TextField()),
                ('answer_b', models.TextField()),
                ('answer_c', models.TextField()),
                ('answer_d', models.TextField()),
                ('chosen_a', models.IntegerField(default=0)),
                ('chosen_b', models.IntegerField(default=0)),
                ('chosen_c', models.IntegerField(default=0)),
                ('chosen_d', models.IntegerField(default=0)),
                ('correct_answer', models.IntegerField(choices=[(0, 'Answer A'), (1, 'Answer B'), (2, 'Answer C'), (3, 'Answer D')])),
                ('difficulty', models.IntegerField(choices=[(0, 'Easy'), (1, 'Intermediate'), (2, 'Challenging'), (3, 'Expert')])),
                ('explanation', models.TextField(help_text='Provide some more context about the right answer and maybe frame it in the larger picture of the other answers. This explanation will be displayed after an answer was picked, irrepective of whether the right or wrong answer was chosen.')),
                ('author', models.CharField(max_length=255)),
            ],
        ),
    ]
