from django.shortcuts import redirect

def session_authenticated(function=None, login_redirect='login'):
    def wrapper(request, *args, **kwargs):
        if request.session.get('authenticated', False):
            return function(request, *args, **kwargs)
        else:
            return redirect(login_redirect)
    return wrapper

    if function:
        return session_authenticated(function)
    return session_authenticated