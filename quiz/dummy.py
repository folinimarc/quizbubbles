from .models import *
import random
from django.contrib.auth.hashers import make_password

def randStr(maxi):
        return ''.join(random.choices(' abcdef ghijklm nopqrs tuvwxyz ', k=random.randint(10, maxi)))

def setup():
    print('start')

    #create space
    space = Space.objects.create(
            name='test',
            password=make_password('test'),
            email='test@test.com'
    )

    questions_per_difficulty = 20

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