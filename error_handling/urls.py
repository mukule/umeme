from django.urls import path
from .views import custom_404, custom_500

app_name = 'error_handling'
urlpatterns = [
    path('404/', custom_404, name='custom_404'),
    path('500/', custom_500, name='custom_500'),
]
