from django.shortcuts import redirect
from .models import Space

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