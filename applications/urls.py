from django.urls import path
from .views import apply_job, apply_job_form, update_status, update_threshold, view_applicants

urlpatterns = [
    path('apply/<int:job_id>/', apply_job, name='apply_job'),
    path('update-status/<int:app_id>/', update_status, name='update_status'),
    path('job/<int:job_id>/update-threshold/', update_threshold, name='update_threshold'),
    path('form/<int:job_id>/', apply_job_form, name='apply_job_form'),
    path('applicants/<int:job_id>/', view_applicants, name='view_applicants'),
]