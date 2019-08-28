from django import forms
from .models import *
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox


class QuestionModelForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('question', 'answer_a', 'answer_b', 'answer_c', 'answer_d', 'correct_answer', 'difficulty', 'explanation', 'contributor')

        labels = {
            'answer_a': 'A)',
            'answer_b': 'B)',
            'answer_c': 'C)',
            'answer_d': 'D)',
        }

        widgets = {
            'question': forms.Textarea(attrs={'rows':2, 'autofocus': 'autofocus'}),
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

class QuizUsernamenameQuiztypeForm(FormErrorsMixin, forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('username', 'quiztype')


class BubbleJoinForm(forms.ModelForm):

    prefix = 'join'
    class Meta:
        model = Bubble
        fields = ('name', 'password')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Bubblename', 'autofocus': 'autofocus'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
            }

    def __init__(self, *args, **kwargs):
        super(BubbleJoinForm, self).__init__(*args, **kwargs)
        self.fields['password'].required = False


class BubbleCreateForm(forms.ModelForm):
    
    password1 = forms.CharField(max_length=20, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(max_length=20, widget=forms.PasswordInput(attrs={'placeholder': 'Repeat password'}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(api_params={'onload': 'adjustHeight'}))

    prefix='create'
    class Meta:
        model = Bubble
        fields = ('name', 'email', 'password1', 'password2', 'public', 'captcha')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Bubblename'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email (public)'}),
            }
        labels = {
            'public': 'Public QuizBubble'
        }

    def clean(self):
        cleaned_data = super(BubbleCreateForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            self.add_error('password2', 'Passwords did not match.')
        bubble = Bubble.objects.filter(name=cleaned_data.get('name', None))
        if bubble and bubble[0].uuid != self.instance.uuid:
            self.add_error('name', 'Name already in use')


class BubbleChangeForm(BubbleCreateForm):

    password2 = forms.CharField(max_length=20, help_text='Leave both blank to keep old password.', widget=forms.PasswordInput(attrs={'placeholder': 'Repeat Password'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['captcha'].required = False


class BubbleDeleteForm(forms.Form):

    delete_confirm = forms.CharField(required=False, help_text='Type "DELETE" to confirm.')
    
    def clean(self):
        cleaned_data = super(BubbleDeleteForm, self).clean()
        if cleaned_data['delete_confirm'] != 'DELETE':
            self.add_error('delete_confirm', 'Type DELETE to confirm.')


class BubblePasswordResetForm(forms.Form):
    password1 = forms.CharField(max_length=20, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(max_length=20, widget=forms.PasswordInput(attrs={'placeholder': 'Repeat password'}))

    def clean(self):
        cleaned_data = super(BubblePasswordResetForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            self.add_error('password2', 'Passwords did not match.')


class BubblePasswordRequestForm(forms.Form):
    captcha = ReCaptchaField()