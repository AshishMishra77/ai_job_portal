from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import User
from jobs.models import Job
from applications.models import Application

from ai_engine.services.parser import extract_text
from ai_engine.services.matcher import compute_score
from ai_engine.services.ollama_client import generate_feedback

# -----------------------
# HOME
# -----------------------
def home(request):
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'base.html', {'jobs': jobs})

# -----------------------
# REGISTER
# -----------------------
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            return render(request, 'users/register.html', {'error': 'Username already exists'})

        User.objects.create_user(username=username, password=password, role=role)
        return redirect('login')

    return render(request, 'users/register.html')

# -----------------------
# LOGIN
# -----------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})

    return render(request, 'users/login.html')

# -----------------------
# LOGOUT
# -----------------------
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# -----------------------
# DASHBOARD
# -----------------------
@login_required
def my_applications(request):
    return Application.objects.filter(candidate=request.user)\
        .select_related('job')\
        .only('status', 'job__title')

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'recruiter':
        # Fetch all jobs posted by this recruiter
        jobs = Job.objects.filter(recruiter=user)
        
        # Fetch applications for these jobs
        applications = Application.objects.filter(job__in=jobs).order_by('-created_at').select_related('candidate', 'job')

        return render(request, 'dashboard/recruiter_dashboard.html', {
            'jobs': jobs,
            'applications': applications,
        })

    elif user.role == 'candidate':
       
        return render(request, 'dashboard/candidate_dashboard.html', {
            'applications' : my_applications(request)
        })
    return redirect('login')

# -----------------------
# JOB APPLICATIONS
# -----------------------
from django.shortcuts import render, redirect, get_object_or_404
@login_required
def apply_job_form(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'applications/apply.html', {'job_id': job_id})

@login_required
def apply_job(request, job_id):
    if request.method == "POST":
        resume = request.FILES.get('resume')
        if not resume:
            return HttpResponse("No file uploaded")

        application = Application.objects.create(
            candidate=request.user,
            job_id=job_id,
            resume=resume
        )

        try:
            resume_text = extract_text(application.resume.path)
            job_text = application.job.description

            application.score = compute_score(resume_text, job_text)
            application.ai_feedback = generate_feedback(resume_text, job_text)
            application.save()
        except Exception as e:
            print("AI Error:", e)

        return redirect('dashboard')

@login_required
def view_applicants(request, job_id):
    applications = Application.objects.filter(job_id=job_id)
    return render(request, 'applications/applicants.html', {'applications': applications})