from django.urls import path
from . import views


app_name = 'main'
urlpatterns = [
    path("", views.index, name="index"),
    path('index/<int:pk>/', views.job_type_detail, name='vacs'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path("bio_info/", views.bio_info, name="bio_info"),
    path('basic_info/<int:user_id>/', views.basic_info, name='basic_info'),
    path('basic_academic/', views.basic_academic, name='basic_academic'),
    path('high_school/', views.high_school, name='high_school'),
    path('college/', views.college, name='college'),
    path('update_basic_education/<int:instance_id>/',
         views.update_basic_academic, name='update_basic_education'),
    path('delete_basic_education/<int:instance_id>/',
         views.delete_basic_academic, name='delete_basic_education'),
    path('further_studies/', views.further_studies, name='further_studies'),
    path('update_further_studies/<int:instance_id>/',
         views.update_further_studies, name='update_further_studies'),
    path('delete_further_studies/<int:instance_id>/',
         views.delete_further_studies, name='delete_further_studies'),
    path('certs/', views.certs, name='certs'),
    path('certification/', views.certification, name='certification'),
    path('update_certification/<int:instance_id>/',
         views.update_certification, name='update_certification'),
    path('delete_certification/<int:instance_id>/',
         views.delete_certification, name='delete_certification'),
    path('memberships/', views.memberships, name='memberships'),
    path('membership/', views.membership, name='membership'),
    path('update_membership/<int:instance_id>/',
         views.update_membership, name='update_membership'),
    path('delete_membership/<int:instance_id>/',
         views.delete_membership, name='delete_membership'),
    path('experience/', views.experience, name='experience'),
    path('work_experience/', views.work_experience, name='work_experience'),
    path('update_work_experience/<int:instance_id>/',
         views.update_work_experience, name='update_work_experience'),
    path('delete_work_experience/<int:instance_id>/',
         views.delete_work_experience, name='delete_work_experience'),
    path('referees/', views.referees, name='referees'),
    path('refs/', views.refs, name='refs'),
    path('update_referees/<int:instance_id>/',
         views.update_referee, name='update_referee'),
    path('delete_referee/<int:instance_id>/',
         views.delete_referee, name='delete_referee'),
    path('career_objective/', views.career_objective, name='career_objective'),
    path('update_career_objective/', views.update_career_objective,
         name='update_career_objective'),
    path('terms/', views.terms, name='terms'),
    path('staff/', views.staff, name='staff_profile'),
    path('update_educational_level/',
         views.update_educational_level, name='edu_level'),
    path('how_to_apply/', views.how, name='how'),
]
