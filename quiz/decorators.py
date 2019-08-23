from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import *


def check_bubble_permission(function=None):
    def wrapper(request, *args, **kwargs):
        bubble_name = kwargs.get('bubble_name', None)
        bubble = get_object_or_404(Bubble, name=bubble_name)
        authenticated = request.session.get(bubble_name, None) == str(bubble.uuid)
        if bubble.public or authenticated:
            return function(request, *args, **kwargs)
        return redirect('login')
    return wrapper
    if function:
        return session_authenticated(function)
    return session_authenticated


def check_question_permission(function=None):
    def wrapper(request, *args, **kwargs):
        bubble_name = kwargs.get('bubble_name', None)
        bubble = get_object_or_404(Bubble, name=bubble_name)
        authenticated = request.session.get(bubble_name, None) == str(bubble.uuid)
        question_id = kwargs.get('question_id', None)
        question = get_object_or_404(Question, id=question_id)
        if authenticated and question.bubble_id == bubble.id:
            return function(request, *args, **kwargs)
        return redirect('login')
    return wrapper
    if function:
        return session_authenticated(function)
    return session_authenticated


def check_quiz_permission(function=None):
    def wrapper(request, *args, **kwargs):
        bubble_name = kwargs.get('bubble_name', None)
        bubble = get_object_or_404(Bubble, name=bubble_name)
        quiz_id = kwargs.get('quiz_id', None)
        quiz = get_object_or_404(Quiz, id=quiz_id)
        authenticated = request.session.get(str(quiz_id), None) == str(quiz.uuid)
        if authenticated and quiz.bubble_id == bubble.id:
            return function(request, *args, **kwargs)
        return redirect('home', bubble_name=bubble_name)
    return wrapper
    if function:
        return session_authenticated(function)
    return session_authenticated