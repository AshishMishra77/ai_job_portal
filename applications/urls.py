from django.urls import path
from .views import apply_job, apply_job_form, view_applicants

urlpatterns = [
    path('apply/<int:job_id>/', apply_job, name='apply_job'),
    path('form/<int:job_id>/', apply_job_form, name='apply_job_form'),
    path('applicants/<int:job_id>/', view_applicants, name='view_applicants'),
]