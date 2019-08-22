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
    nr_spaces = 60
    questions_per_difficulty = 20

    print('start')

    #create spaces
    for k in range(nr_spaces):
        print(f'Create space {k}')
        Space.objects.create(
            name=randStr(20, slug=True),
            password=make_password('pw'),
            email='test@test.com',
            public=True if random.random() < 0.5 else False
        )

    spaces = Space.objects.all()
    for k, space in enumerate(spaces):
        print(f'---- {space.name} ({k+1}/{len(spaces)}) -----')
        for difficulty in Question.DIFFICULTIES:
            print(f'---- {difficulty[0]} -----')
            for k in range(questions_per_difficulty):
                Question.objects.create(
                    question=randStr(400),
                    answer_a=randStr(160),
                    answer_b=randStr(160),
                    answer_c=randStr(160),
                    answer_d=randStr(160),
                    correct_answer=Question.ANSWER_A,
                    difficulty=difficulty[0],
                    explanation=randStr(400),
                    contributor='fom',
                    space_id=space.id
                )

    print('finished')