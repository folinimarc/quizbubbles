from django.contrib import admin
from .models import *
from django.forms import widgets

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': widgets.Textarea(attrs={'rows':4, 'cols': 40})},
    }
    list_select_related = ('bubble',)
    list_display = ('pk', 'trimmed_question', 'difficulty', 'contributor', 'bubble')
    search_fields = ('pk', 'trimmed_question', 'difficulty', 'contributor', 'bubble')

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

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid',)
    list_select_related = ('bubble',)
    list_display = ('id', 'username', 'quiztype', 'questions_total', 'active', 'duration', 'enddatetime', 'last_access','bubble')
    search_fields = ('username', 'quiztype', 'questions_total', 'active', 'duration', 'enddatetime', 'last_access', 'bubble')


@admin.register(Bubble)
class BubbleAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created', 'last_access')
    readonly_fields = ('uuid', 'password')