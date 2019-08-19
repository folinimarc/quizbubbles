from django import forms
from .models import *


class QuestionModelForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ('chosen_a', 'chosen_b', 'chosen_c', 'chosen_d', 'space')

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


class FormErrorsMixin:
    def get_form_errors_as_string(self):
        if not self.cleaned_data:
            self.is_valid()
        return ' '.join([' '.join(set([x for l in self.errors.values() for x in l]))])

class GamePlayernameGametypeForm(FormErrorsMixin, forms.ModelForm):
    class Meta:
        model = Game
        fields = ('player', 'gametype')


class SpaceJoinForm(forms.ModelForm):

    prefix = 'join'
    class Meta:
        model = Space
        fields = ('name', 'password')
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
            'name': forms.TextInput(attrs={'placeholder': 'Spacename'}),
            }


class SpaceCreateForm(forms.ModelForm):
    
    password1 = forms.CharField(max_length=20, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(max_length=20, widget=forms.PasswordInput(attrs={'placeholder': 'Repeat password'}))

    prefix='create'
    class Meta:
        model = Space
        fields = ('name', 'email')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Spacename'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email'}),
            }

    def clean(self):
        cleaned_data = super(SpaceCreateForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            self.add_error('password2', 'Passwords did not match.')