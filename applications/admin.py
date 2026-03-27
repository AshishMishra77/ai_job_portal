# applications/admin.py

from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'status', 'score', 'created_at')  # Columns in list view
    list_filter = ('status', 'created_at', 'job')                          # Filters in sidebar
    search_fields = ('candidate__username', 'job__title')                  # Search by candidate or job
    ordering = ('-created_at',)                                            # Show newest first