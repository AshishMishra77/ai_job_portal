from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import threading

from applications.models import Application
from jobs.models import Job
from ai_engine.services.parser import extract_text
from ai_engine.services.matcher import compute_score
from ai_engine.services.ollama_client import generate_feedback


# -----------------------
# APPLY FORM (HTMX)
# -----------------------
@login_required
def apply_job_form(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'applications/apply.html', {'job': job})


# -----------------------
# BACKGROUND AI PROCESS
# -----------------------
def process_ai(application):
    try:
        if not application.resume:
            return

        resume_path = application.resume.path

        print("Resume Path:", resume_path)  # DEBUG

        resume_text = extract_text(resume_path)
        job_text = application.job.description or ""

        score = compute_score(resume_text, job_text)
        feedback = generate_feedback(resume_text, job_text)

        application.score = score
        application.ai_feedback = feedback
        application.status = 'processed'
        application.save()

    except Exception as e:
        print("AI ERROR:", str(e))


# -----------------------
# APPLY JOB
# -----------------------
@login_required
def apply_job(request, job_id):
    if request.method != "POST":
        return HttpResponse("Invalid request method", status=405)

    job = get_object_or_404(Job, id=job_id)

    # ❗ Prevent duplicate applications
    if Application.objects.filter(candidate=request.user, job=job).exists():
        return HttpResponse("You have already applied for this job.")

    uploaded_resume = request.FILES.get('resume')

    # Resume fallback
    resume_file = uploaded_resume or getattr(request.user, 'resume', None)

    if not resume_file:
        return HttpResponse("Please upload a resume", status=400)

    application = Application.objects.create(
        candidate=request.user,
        job=job,
        resume=resume_file,
        status='pending',
    )

    # 🔥 Run AI in background (NON-BLOCKING)
    # threading.Thread(target=process_ai, args=(application,)).start()
    process_ai(application)

    # HTMX response
    if request.headers.get("HX-Request") == "true":
        return render(request, 'applications/success.html')

    return redirect('dashboard')


# -----------------------
# VIEW APPLICANTS (RECRUITER)
# -----------------------
@login_required
def view_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    applications = Application.objects.filter(job=job).select_related('candidate')

    # 🔥 Filter by score (Week 4 feature)
    min_score = request.GET.get('min_score')
    if min_score:
        applications = applications.filter(score__gte=min_score)

    # 🔥 Sort by score (top candidates first)
    applications = applications.order_by('-score', '-created_at')

    return render(request, 'applications/applicants.html', {
        'job': job,
        'applications': applications
    })