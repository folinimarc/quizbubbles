from django.db import models
import json

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
    chosen_answers_count = models.TextField(default=json.dumps({'a':0, 'b':0, 'c':0, 'd':0}))
    correct_answer = models.CharField(max_length=1, choices=ANSWERS)
    difficulty = models.IntegerField(choices=DIFFICULTIES)
    explanation = models.TextField(help_text='Provide some more context about the right answer and maybe frame it in the larger picture of the other answers. This explanation will be displayed after an answer was picked, irrepective of whether the right or wrong answer was chosen.')
    contributor = models.CharField(max_length=255)
    bubble = models.ForeignKey('Bubble', on_delete=models.CASCADE, related_name='questions')
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_verbose_difficulty_from_dbvalue(db_value):
        for db_val, verbose in Question.DIFFICULTIES:
            if db_value == db_val:
                return verbose
        return None

    @property
    def trimmed_question(self):
        return f'{self.question[:200]}...' if len(self.question) > 10 else str(self.question)

    def __str__(self):
        return f'Q{self.pk} - {self.question[:10]}'

class Quiz(models.Model):
    SPRINT = 0
    MARATHON = 1
    QUIZTYPE = (
        (SPRINT, 'Sprint'),
        (MARATHON, 'Marathon'),
    )

    INITIALIZED = 0
    IN_PROGRESS = 1
    FINISHED = 2
    QUIZSTATE = (
        (INITIALIZED, 'Initialized'),
        (IN_PROGRESS, 'In progress'),
        (FINISHED, 'Finished')
    )

    quiztype = models.IntegerField(choices=QUIZTYPE)
    quizstate = models.IntegerField(choices=QUIZSTATE, default=INITIALIZED)
    username = models.CharField(max_length=20)
    questions_index = models.IntegerField(default=0)
    questions_answered = models.IntegerField(default=0)
    questions_total = models.IntegerField(default=0)
    question_ids = models.TextField()
    startdatetime = models.DateTimeField(auto_now_add=True)
    enddatetime = models.DateTimeField(null=True, blank=True)
    last_access = models.DateTimeField(auto_now=True)
    helperdatetime = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0)
    bubble = models.ForeignKey('Bubble', on_delete=models.CASCADE, related_name='quizes')
    joker_fiftyfifty_available = models.BooleanField(default=True)
    joker_audience_available = models.BooleanField(default=True)
    joker_timestop_available = models.BooleanField(default=True)
    timestop_active = models.BooleanField(default=False)
    can_send_love = models.BooleanField(default=True)
    heartbeat_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Quiz {self.id}'

class Bubble(models.Model):
    name = models.SlugField(max_length=20)
    email = models.EmailField()
    password = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    last_access = models.DateTimeField(auto_now=True)
    last_contribution = models.DateTimeField(null=True, blank=True)
    public = models.BooleanField(default=False)
    reset_token = models.TextField(null=True, blank=True)
    hearts = models.IntegerField(default=0)
    last_cleanup = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name