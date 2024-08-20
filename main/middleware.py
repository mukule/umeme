import datetime
from django.conf import settings
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages

class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        now = datetime.datetime.now()
        last_activity = request.session.get('last_activity')

        # If last_activity is a string, convert it to a datetime object
        if isinstance(last_activity, str):
            last_activity = datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S.%f')
        elif last_activity is None:
            last_activity = now  # Set to now if it's not in the session

        # Time limit in seconds (e.g., 30 minutes)
        expiry_seconds = getattr(settings, 'AUTO_LOGOUT_DELAY', 1800)

        if (now - last_activity).seconds > expiry_seconds:
            logout(request)
            messages.info(
            request, "You have been Auto logged out due to Inactivity for long.")
            return redirect('users:login')

        # Store the last activity as a string
        request.session['last_activity'] = now.strftime('%Y-%m-%d %H:%M:%S.%f')
