from django import forms
from .models import *


class QuestionModelForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ('chosen_a', 'chosen_b', 'chosen_c', 'chosen_d')

        labels = {
            'answer_a': 'A)',
            'answer_b': 'B)',
            'answer_c': 'C)',
            'answer_d': 'D)',
        }

        widgets = {
            'question': forms.Textarea(attrs={'rows':2}),
            'answer_a': forms.Textarea(attrs={'rows':1}),
            'answer_b': forms.Textarea(attrs={'rows':1}),
            'answer_c': forms.Textarea(attrs={'rows':1}),
            'answer_d': forms.Textarea(attrs={'rows':1}),
            'explanation': forms.Textarea(attrs={'rows':4}),
        }


class GamePlayernameGametypeForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('player', 'gametype')