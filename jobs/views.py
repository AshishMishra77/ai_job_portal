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

        # Basic validation
        if not title or not description:
            return render(request, 'jobs/create_job.html', {
                'error': 'Title and Description are required'
            })

        Job.objects.create(
            title=title,
            description=description,
            skills=skills,
            recruiter=request.user
        )

        return redirect('jobs')

    return render(request, 'jobs/create_job.html')