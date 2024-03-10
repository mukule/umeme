from django.urls import path
from . import views

app_name = 'hr'
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("system_users/", views.system_users, name="system_users"),
    path("job_types/", views.job_types, name="job_types"),
    path("create_job_type", views.create_job_type,
         name="create_job_type"),
    path('edit/<int:job_type_id>/', views.edit_job_type, name='edit_job_type'),
    path('delete/<int:job_type_id>/',
         views.delete_job_type, name='delete_job_type'),
    path("jobs/", views.jobs, name="jobs"),
    path("create_job/", views.create_job, name="create_job"),
    path('job_detail/<int:vacancy_id>/', views.job_detail, name='job_detail'),
    path('publish/<int:job_id>/', views.publish, name='publish'),
    path('edit_job/<int:job_id>/', views.edit_job, name='edit_job'),
    path('delete_job/<int:job_id>/', views.delete_job, name='delete_job'),
    path("applications/", views.applications, name="applications"),
    path('application_details/<int:vacancy_id>/',
         views.application_detail, name='application_detail'),
    path('shortlist/<int:vacancy_id>/<int:application_id>/',
         views.toggle_shortlist, name='shortlist'),
    path('applicant_resume/<int:user_id>/',
         views.resume, name='applicant_resume'),
    path('application_detail/<int:vacancy_id>/<str:filter_criteria>/',
         views.application_detail, name='application_detail_with_filter'),
    path("create_job_discipline", views.create_job_discipline,
         name="create_job_discipline"),
    path("job_disciplines", views.job_disciplines, name="job_disciplines"),
    path('update_job_discipline/<int:job_discipline_id>/',
         views.update_job_discipline, name='update_job_discipline'),
    path('delete_job_discipline/<int:job_discipline_id>/',
         views.delete_job_discipline, name='delete_job_discipline'),
    path("create_certifying_body", views.create_certifying_body,
         name="create_certifying_body"),
    path("certifying_bodies", views.certifying_bodies, name="certifying_bodies"),
    path('edit_certifying_body/<int:certifying_body_id>/',
         views.edit_certifying_body, name='edit_certifying_body'),
    path('delete_certifying_body/<int:certifying_body_id>/',
         views.delete_certifying_body, name='delete_certifying_body'),
    path("create_certificate", views.create_certificate, name="create_certificate"),
    path("certificates", views.certificates, name="certificates"),
    path('certificates/edit/<int:certificate_id>/',
         views.edit_certificate, name='edit_certificate'),
    path('certificates/delete/<int:certificate_id>/',
         views.delete_certificate, name='delete_certificate'),
    path('fields-of-study/', views.fields_of_study, name='fields_of_study'),
    path('fields-of-study/create/', views.create_field_of_study,
         name='create_field_of_study'),
    path('fields-of-study/edit/<int:field_of_study_id>/',
         views.edit_field_of_study, name='edit_field_of_study'),
    path('fields-of-study/delete/<int:field_of_study_id>/',
         views.delete_field_of_study, name='delete_field_of_study'),
    path('edu_levels/', views.edu_levels, name='edu_levels'),
    path('create_ethnicity/', views.create_ethnicity, name='create_ethnicity'),
    path('ethnicities/', views.ethnicities, name='ethnicities'),
    path('edit/<int:ethnicity_id>/', views.edit_ethnicity, name='edit_ethnicity'),
    path('delete/<int:ethnicity_id>/',
         views.delete_ethnicity, name='delete_ethnicity'),
    path('user_access_logs/', views.user_access_logs, name='user_logs'),
    path('admin_access_logs/', views.admin_access_logs, name='admin_logs'),
    path('portal_reports/', views.portal_reports, name='portal_reports'),
    path('vacancy_report/', views.vacancy_report, name='vacancy_report'),
    path('applications_reports/', views.applications_reports,
         name='applications_reports'),
    path('application_report/<int:vacancy_id>/',
         views.application_report, name='application_report'),
    path('adms/', views.adms, name='adms'),
    path('admin/register/', views.admin_register, name='admin_reg'),
    path('create_terms/', views.create_terms, name='create_terms'),
    path('staffs/', views.staffs, name='kgn_staffs'),
    path('import_excel/', views.import_excel, name='import_excel'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_staff'),
    path('delete_staff/<int:user_id>/',
         views.delete_staff, name='delete_staff'),
    path('reset_trials/<int:user_id>/', views.reset_trials, name='reset_trials'),
    path('delete_users/', views.delete_users_with_access_level_5,
         name='delete_users-staffs'),
    path('hr_admins/', views.hr_admin,
         name='hr_admins'),
    path('admins/<int:admin_id>/', views.admin_role, name='admin_role'),

]
