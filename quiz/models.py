from django.db import models
import uuid

class Question(models.Model):

    ANSWER_A = 'a'
    ANSWER_B = 'b'
    ANSWER_C = 'c'
    ANSWER_D = 'd'
    ANSWERS = (
        (ANSWER_A, 'Answer A'),
        (ANSWER_B, 'Answer B'),
        (ANSWER_C, 'Answer C'),
        (ANSWER_D, 'Answer D'),
    )

    EASY = 0
    INTERMEDIATE = 1
    CHALLENGING = 2
    EXPERT = 3
    DIFFICULTIES = (
        (EASY, 'Easy'),
        (INTERMEDIATE, 'Intermediate'),
        (CHALLENGING, 'Challenging'),
        (EXPERT, 'Expert'),
    )

    question = models.TextField()
    answer_a = models.TextField()
    answer_b = models.TextField()
    answer_c = models.TextField()
    answer_d = models.TextField()
    chosen_a = models.IntegerField(default=0)
    chosen_b = models.IntegerField(default=0)
    chosen_c = models.IntegerField(default=0)
    chosen_d = models.IntegerField(default=0)
    correct_answer = models.CharField(max_length=1, choices=ANSWERS)
    difficulty = models.IntegerField(choices=DIFFICULTIES)
    explanation = models.TextField(help_text='Provide some more context about the right answer and maybe frame it in the larger picture of the other answers. This explanation will be displayed after an answer was picked, irrepective of whether the right or wrong answer was chosen.')
    author = models.CharField(max_length=255)

    def trimmed_question(self):
        return f'{self.question[:10]}...' if len(self.question) > 10 else str(self.question)

    def __str__(self):
        return f'Q{self.pk} - {self.question[:10]}'

class Game(models.Model):
    SPRINT = 0
    MARATHON = 1
    GAMETYPE = (
        (SPRINT, 'Sprint'),
        (MARATHON, 'Marathon'),
    )

    uuid = models.UUIDField(default=uuid.uuid4)
    gametype = models.IntegerField(choices=GAMETYPE)
    active = models.BooleanField(default=True)
    player = models.CharField(max_length=30)
    questions_answered = models.IntegerField(default=0)
    question_ids = models.TextField()
    startdatetime = models.DateTimeField(auto_now_add=True)
    enddatetime = models.DateTimeField(auto_now=True)
    helperdatetime = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0)
    intermezzo_state = models.BooleanField(default=True)
