from .models import *
import random
from django.contrib.auth.hashers import make_password

def randStr(maxi, slug=False):
        if slug:
            letter_set = 'abcdefghijklmnopqrstuvwxyz'
        else:
            letter_set= ' abcdef ghijklm nopqrs tuvwxyz '
        return ''.join(random.choices(letter_set, k=random.randint(10, maxi)))

def setup():
    nr_bubbles = 60
    questions_per_difficulty = 20

    print('start')

    #create bubbles
    for k in range(nr_bubbles):
        print(f'Create bubble {k}')
        Bubble.objects.create(
            name=randStr(20, slug=True),
            password=make_password('pw'),
            email='test@test.com',
            public=True if random.random() < 0.5 else False
        )

    bubbles = Bubble.objects.all()
    for k, bubble in enumerate(bubbles):
        print(f'---- {bubble.name} ({k+1}/{len(bubbles)}) -----')
        for difficulty in Question.DIFFICULTIES:
            print(f'---- {difficulty[0]} -----')
            for k in range(questions_per_difficulty):
                Question.objects.create(
                    question=randStr(400),
                    answer_a='A:' + randStr(160),
                    answer_b='B:' + randStr(160),
                    answer_c='C:' + randStr(160),
                    answer_d='D:' + randStr(160),
                    correct_answer=Question.ANSWER_A,
                    difficulty=difficulty[0],
                    explanation=randStr(400),
                    contributor='fom',
                    bubble_id=bubble.id
                )

    print('finished')