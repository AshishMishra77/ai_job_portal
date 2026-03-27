from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'recruiter', 'created_at')  # Columns to display in admin list view
    list_filter = ('created_at', 'recruiter')            # Filters in the sidebar
    search_fields = ('title', 'description', 'skills')  # Searchable fields
    ordering = ('-created_at',)                          # Default ordering