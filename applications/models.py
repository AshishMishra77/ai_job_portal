from django.db import models
from django.conf import settings
from jobs.models import Job
# from applications.models import Application
from jobs.models import Job
# from users.models import User


# applications/models.py
class Application(models.Model):
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='applications/resumes/')
    score = models.FloatField(null=True, blank=True)
    ai_feedback = models.TextField(blank=True)
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # ✅ default

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.username} - {self.job.title}"