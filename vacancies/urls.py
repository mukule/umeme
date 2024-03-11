from django.urls import path
from . import views

app_name = 'vacancies'
urlpatterns = [
    path('job/<int:vacancy_id>/', views.job, name='job'),
    path("internships", views.internships, name="internships"),
    path('internship/<int:vacancy_id>/', views.internship, name='internship'),
    path("attachments", views.attachments, name="attachments"),
    path('attachment/<int:vacancy_id>/', views.attachment, name='attachment'),
    path('apply/<int:vacancy_id>/', views.apply, name='apply'),
    path('applications/', views.applications, name='applications'),
    path('reapply/<int:application_id>/',
         views.reapply_application, name='recall_application'),
    path('delete/<int:application_id>/',
         views.delete_application, name='delete_application'),
    path("internal", views.internal, name="internal"),
    path('internal_detail/<int:vacancy_id>/',
         views.internal_detail, name='internal_detail'),
    path('application/success/', views.application_succ, name='apply_succ'),
    path('vacancies/apply_fail', views.apply_fail, name='apply_fail'),

]
