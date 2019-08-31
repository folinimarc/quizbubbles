from django.contrib import admin
from .models import *
from django.forms import widgets
from django.contrib.auth.hashers import make_password
from django.db.models import Count

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': widgets.Textarea(attrs={'rows':4, 'cols': 40})},
    }
    list_select_related = ('bubble',)
    list_display = ('pk', 'trimmed_question', 'difficulty', 'contributor', 'bubble')
    search_fields = ('pk', 'question', 'answer_a', 'answer_b', 'answer_c', 'answer_d', 'explanation', 'difficulty', 'contributor', 'bubble__name')

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
    list_select_related = ('bubble',)
    list_display = ('id', 'username', 'quiztype', 'questions_total', 'questions_answered','quizstate', 'duration', 'enddatetime', 'last_access','bubble')
    search_fields = ('username', 'quiztype', 'questions_total', 'questions_answered', 'quizstate', 'duration', 'enddatetime', 'last_access', 'bubble__name')


@admin.register(Bubble)
class BubbleAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _nr_questions=Count('questions', distinct=True),
            _nr_quizes=Count('quizes', distinct=True),
        )
        return queryset

    def nr_questions(self, obj):
        return obj.questions.count()

    def nr_quizes(self, obj):
        return obj.quizes.count()

    def get_form(self, request, obj=None, **kwargs):
        form = super(BubbleAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['password'].help_text = 'Passwords are not stored in clean text. To set a new password just enter it and save the model. Do not be confused if you see gibberish again next time you reload the model as the password gets hashed.'
        return form

    def save_model(self, request, obj, form, change):
        if form.changed_data and 'password' in form.changed_data:
            obj.password = make_password(form.cleaned_data['password'])
            obj.save()
        return super(BubbleAdmin, self).save_model(request, obj, form, change)

    list_display = ('name', 'email', 'public', 'hearts', 'nr_questions', 'nr_quizes', 'created', 'last_contribution', 'last_access')
    readonly_fields = ('reset_token',)
    search_fields = ('name', 'email', 'public', 'hearts', 'created', 'last_contribution', 'last_access')

    nr_questions.admin_order_field = '_nr_questions'
    nr_quizes.admin_order_field = '_nr_quizes'
