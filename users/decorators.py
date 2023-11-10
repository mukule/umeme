from django.shortcuts import redirect

def user_not_authenticated(function=None, redirect_url='/'):
    """
    Decorator for views that checks that the user is NOT logged in, redirecting
    to the homepage if necessary by default.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)
                
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)

    return decorator


def access_level_check(user_access_level, redirect_view_name):
    def decorator(view_func):
        def wrapped(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.access_level == user_access_level:
                return redirect(redirect_view_name)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def system_admin_required(view_func):
    def wrapped(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.function == 1 or request.user.is_superuser:  # Check for System Admin
            return view_func(request, *args, **kwargs)
        return redirect('users:denials')  # Redirect to an error view if not authorized
    return wrapped

def system_admin_required(view_func):
    def wrapped(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.function in (1, 2) or request.user.is_superuser:  # Check for System Admin or HR functions
            return view_func(request, *args, **kwargs)
        return redirect('users:denials')  # Redirect to an error view if not authorized
    return wrapped

def system_admin_hr_required(view_func):
    def wrapped(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.function in (1, 2, 3) or request.user.is_superuser:  # Check for System Admin, HR, or Post functions
            return view_func(request, *args, **kwargs)
        return redirect('users:denials')
    return wrapped

def system_admin_hr_publish_required(view_func):
    def wrapped(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.function in (1, 2, 4) or request.user.is_superuser:  # Check for System Admin, HR, or Publish functions
            return view_func(request, *args, **kwargs)
        return redirect('users:denials')
    return wrapped

def system_admin_hr_shortlist_required(view_func):
    def wrapped(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.function in (1, 2, 5) or request.user.is_superuser:  # Check for System Admin, HR, or Shortlist functions
            return view_func(request, *args, **kwargs)
        return redirect('users:denials')
    return wrapped


def admins(view_func):
    def wrapped(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.function in (1, 2, 3, 4, 5) or request.user.is_superuser:  # Check for System Admin, HR, or Shortlist functions
            return view_func(request, *args, **kwargs)
        return redirect('users:denials')
    return wrapped

