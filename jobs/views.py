from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Job


# -----------------------
# JOB LIST
# -----------------------
@login_required
def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')

    return render(request, 'jobs/jobs.html', {
        'jobs': jobs
    })


# -----------------------
# CREATE JOB (RECRUITER ONLY)
# -----------------------
@login_required
def create_job(request):

    if request.user.role != 'recruiter':
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        skills = request.POST.get('skills')
        threshold_enabled = request.POST.get('threshold_enabled') == 'on'
        
        ats_threshold = request.POST.get('ats_threshold')
        try:
            ats_threshold = float(ats_threshold) if ats_threshold else 60.0
        except ValueError:
            ats_threshold = 60.0

        # Basic validation
        if not title or not description:
            return render(request, 'jobs/create_job.html', {
                'error': 'Title and Description are required'
            })

        Job.objects.create(
            title=title,
            description=description,
            skills=skills,
            recruiter=request.user,
            ats_threshold = ats_threshold,
            threshold_enabled = threshold_enabled,
            
        )

        return redirect('jobs')

    return render(request, 'jobs/create_job.html')