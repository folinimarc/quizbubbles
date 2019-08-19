from django.contrib import admin
from .models import *
from django.forms import widgets

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': widgets.Textarea(attrs={'rows':4, 'cols': 40})},
    }
    list_select_related = ('space',)
    list_display = ('pk', 'trimmed_question', 'difficulty', 'contributor', 'space')
    search_fields = ('pk', 'trimmed_question', 'difficulty', 'contributor', 'space')

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
    readonly_fields = ('uuid',)
    list_select_related = ('space',)
    list_display = ('id', 'player', 'gametype', 'questions_total', 'active', 'duration', 'enddatetime', 'last_access','space')
    search_fields = ('player', 'gametype', 'questions_total', 'active', 'duration', 'enddatetime', 'last_access', 'space')


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created', 'last_access')
    readonly_fields = ('uuid', 'password')