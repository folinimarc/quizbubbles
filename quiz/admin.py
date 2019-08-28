from django.contrib import admin
from .models import *
from django.forms import widgets
from django.contrib.auth.hashers import make_password

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
    list_display = ('name', 'email', 'public', 'hearts', 'created', 'last_access')
    readonly_fields = ('uuid', 'reset_token')

    def get_form(self, request, obj=None, **kwargs):
        form = super(BubbleAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['password'].help_text = 'Passwords are not stored in clean text. To set a new password just enter it and save the model. Do not be confused if you see gibberish again next time you reload the model as the password gets hashed.'
        return form

    def save_model(self, request, obj, form, change):
        if form.changed_data and 'password' in form.changed_data:
            obj.password = make_password(form.cleaned_data['password'])
            obj.save()
        return super(BubbleAdmin, self).save_model(request, obj, form, change)