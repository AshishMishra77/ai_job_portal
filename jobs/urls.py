from django.urls import path
from .views import job_list, create_job

urlpatterns = [
    path('', job_list, name='jobs'),
    path('create/', create_job, name='create_job'),
]