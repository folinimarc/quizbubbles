from django.shortcuts import redirect, get_object_or_404
from .models import *

def session_authenticated(function=None, login_redirect='login'):
    def wrapper(request, *args, **kwargs):
        spaceid = request.session.get('spaceid', False)
        if Space.objects.filter(uuid=spaceid).exists():
            return function(request, *args, **kwargs)
        return redirect(login_redirect)
    return wrapper

    if function:
        return session_authenticated(function)
    return session_authenticated


def questionedit_authenticated(function=None, login_redirect='login'):
    def wrapper(request, question_id, *args, **kwargs):
        spaceid = request.session.get('spaceid', False)
        if Space.objects.filter(uuid=spaceid).exists():
            if str(get_object_or_404(Question, id=question_id).space.uuid) == spaceid:
                return function(request, question_id, *args, **kwargs)
        return redirect(login_redirect)
    return wrapper

    if function:
        return session_authenticated(function)
    return session_authenticated