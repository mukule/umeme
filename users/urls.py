from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'users'
urlpatterns = [
    path("register/", views.register, name="register"),
    path('login/', views.custom_login, name='login'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('logout', views.custom_logout, name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('secure/<uidb64>/<token>', views.secure, name='secure'),
    path("password_change", views.password_change, name="password_change"),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('reset/<uidb64>/<token>', views.passwordResetConfirm,
         name='password_reset_confirm'),
    path("not_authorized/", views.not_authorized, name="not_authorized"),
    path('create_staff/', views.create_access_level_5_user, name='create_staff'),
    path("staff_no/", views.staff_no, name="staff_no"),
    path("permission_denied/", views.not_allowed, name="denials"),
    path("f_pass", views.f_pass, name="f_pass"),
    path('del_user/<int:user_id>', views.delete_user, name='del_user'),
    path('terms_acceptance/',
         views.terms_acceptance, name='terms_acceptance'),
    path('vacancy/<int:vacancy_id>/terms_acceptance/',
         views.internal_terms_acceptance, name='internal_terms_acceptance'),
    path('internship/<int:vacancy_id>/terms_acceptance/',
         views.internship_terms_acceptance, name='internship_terms_acceptance'),
    path('attachment/<int:vacancy_id>/terms_acceptance/',
         views.attachment_terms_acceptance, name='attachment_terms_acceptance'),
]
