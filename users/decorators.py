from django.shortcuts import redirect
from django.urls import reverse


def user_not_authenticated(view_func):
    """
    Decorator for views that checks if the user is NOT logged in.
    Redirects to 'users:denials' if the user is authenticated.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('users:logout'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admins(view_func):
    """
    Decorator for views that checks if the user is authenticated and
    either has access level 5 or is a superuser. Redirects to 'users:denials'
    if the user does not meet these conditions.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.access_level == 5 or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        return redirect(reverse('users:denials'))
    return _wrapped_view


def general(view_func):
    """
    Decorator for views that checks if the user has function 10 (ICT),
    is a superuser, or has function 1 (General HR). Redirects to 'users:denials'
    if the user does not meet these conditions.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (
            request.user.function == 10 or
            request.user.is_superuser or
            request.user.function == 1
        ):
            return view_func(request, *args, **kwargs)
        return redirect(reverse('users:denials'))
    return _wrapped_view


def postone(view_func):

    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (
            request.user.function == 10 or
            request.user.is_superuser or
            request.user.function == 1 or
            request.user.function == 2
        ):
            return view_func(request, *args, **kwargs)
        return redirect(reverse('users:denials'))
    return _wrapped_view


def posttwo(view_func):

    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (
            request.user.function == 10 or
            request.user.is_superuser or
            request.user.function == 1 or
            request.user.function == 3
        ):
            return view_func(request, *args, **kwargs)
        return redirect(reverse('users:denials'))
    return _wrapped_view


def access_level_check(user_access_level, redirect_view_name):
    def decorator(view_func):
        def wrapped(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.access_level == user_access_level:
                return redirect(redirect_view_name)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def staffs(view_func):
    """
    Decorator for views that checks if the user has access level 5 or is a superuser.
    Redirects to 'users:denials' if the user does not meet these conditions.
    """
    def wrapped(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.access_level == 5:
                return view_func(request, *args, **kwargs)
        return redirect(reverse('users:denials'))

    return wrapped
