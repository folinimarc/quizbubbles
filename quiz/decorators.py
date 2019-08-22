from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import *


def check_space_permission(function=None):
    def wrapper(request, *args, **kwargs):
        space_name = kwargs.get('space_name', None)
        space = get_object_or_404(Space, name=space_name)
        authenticated = request.session.get(space_name, None) == str(space.uuid)
        if space.public or authenticated:
            return function(request, *args, **kwargs)
        return redirect('login')
    return wrapper
    if function:
        return session_authenticated(function)
    return session_authenticated


def check_question_permission(function=None):
    def wrapper(request, *args, **kwargs):
        space_name = kwargs.get('space_name', None)
        space = get_object_or_404(Space, name=space_name)
        authenticated = request.session.get(space_name, None) == str(space.uuid)
        question_id = kwargs.get('question_id', None)
        question = get_object_or_404(Question, id=question_id)
        if authenticated and question.space_id == space.id:
            return function(request, *args, **kwargs)
        return redirect('login')
    return wrapper
    if function:
        return session_authenticated(function)
    return session_authenticated


def check_quiz_permission(function=None):
    def wrapper(request, *args, **kwargs):
        space_name = kwargs.get('space_name', None)
        space = get_object_or_404(Space, name=space_name)
        quiz_id = kwargs.get('quiz_id', None)
        quiz = get_object_or_404(Quiz, id=quiz_id)
        authenticated = request.session.get(str(quiz_id), None) == str(quiz.uuid)
        if authenticated and quiz.space_id == space.id:
            return function(request, *args, **kwargs)
        return redirect('home', space_name=space_name)
    return wrapper
    if function:
        return session_authenticated(function)
    return session_authenticated