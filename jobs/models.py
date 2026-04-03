from django.db import models
from users.models import User

class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    skills = models.TextField()
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE)
    ats_threshold = models.FloatField(default=60.0)
    threshold_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title