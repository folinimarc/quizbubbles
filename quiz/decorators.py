from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import *


def check_bubble_permission(authenticated_only=False):
    def outer(function=None):
        def wrapper(request, *args, **kwargs):
            bubble_name = kwargs.get('bubble_name', None)
            bubble = get_object_or_404(Bubble, name=bubble_name)
            authenticated = request.session.get(bubble_name, None) == str(bubble.uuid)
            if (not authenticated_only and bubble.public) or authenticated:
                return function(request, *args, **kwargs)
            messages.info(request, f'You tried to access a ressource without the necessary permissions. Please log in!')
            return redirect('login')
        return wrapper
    return outer


def check_question_permission(function=None):
    def wrapper(request, *args, **kwargs):
        bubble_name = kwargs.get('bubble_name', None)
        bubble = get_object_or_404(Bubble, name=bubble_name)
        authenticated = request.session.get(bubble_name, None) == str(bubble.uuid)
        question_id = kwargs.get('question_id', None)
        question = get_object_or_404(Question, id=question_id)
        if authenticated and question.bubble_id == bubble.id:
            return function(request, *args, **kwargs)
        messages.info(request, f'You tried to access a ressource without the necessary permissions. Please log in!')
        return redirect('login')
    return wrapper


def check_quiz_permission(function=None):
    def wrapper(request, *args, **kwargs):
        bubble_name = kwargs.get('bubble_name', None)
        bubble = get_object_or_404(Bubble, name=bubble_name)
        quiz_id = kwargs.get('quiz_id', None)
        quiz = get_object_or_404(Quiz, id=quiz_id)
        authenticated = request.session.get(str(quiz_id), None) == str(quiz.uuid)
        if authenticated and quiz.bubble_id == bubble.id:
            return function(request, *args, **kwargs)
        messages.info(request, f'You tried to access a ressource without the necessary permissions. Please log in!')
        return redirect('login')
    return wrapper


def human_confirmed(function=None):
    def wrapper(request, *args, **kwargs):
        if request.session.get('human_confirmed', False):
            return function(request, *args, **kwargs)
        messages.info(request, f'You tried to access a ressource without the necessary permissions. Please log in!')
        return redirect('login')
    return wrapper