from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('candidate', 'Candidate'),
        ('recruiter', 'Recruiter'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # Profile Resume
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)

    # AI / Profile Data
    skills = models.TextField(blank=True)
    experience = models.IntegerField(null=True, blank=True)

    def is_candidate(self):
        return self.role == 'candidate'

    def is_recruiter(self):
        return self.role == 'recruiter'

    def __str__(self):
        return f"{self.username} ({self.role})"