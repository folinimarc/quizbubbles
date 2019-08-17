from django.contrib import admin
from .models import *
from django.forms import widgets

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': widgets.Textarea(attrs={'rows':4, 'cols': 40})},
    }

    list_display = ('pk', 'trimmed_question', 'difficulty', 'author')

    fieldsets = (
        ('Define question and answers', {
            'fields': (
                ('question',),
                ('answer_a', 'answer_b'),
                ('answer_c', 'answer_d'),
            )
        }),
        ('Define correct answer, difficulty and explanation', {
            'fields': (
                ('difficulty', 'correct_answer'),
                'explanation'
            )
        }),
    )

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    pass