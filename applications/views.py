from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

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
def update_status(request, app_id):
    application = get_object_or_404(Application, id=app_id)

    # 🔐 Only recruiter can update
    if application.job.recruiter != request.user:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        new_status = request.POST.get('status')

        # ✅ Validate status
        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.save()

    return redirect('view_applicants', job_id=application.job.id)

@login_required
def update_threshold(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # 🔐 Only recruiter can change settings
    if job.recruiter != request.user:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        threshold = request.POST.get("ats_threshold")
        enabled = request.POST.get("threshold_enabled")

        # ✅ Update threshold safely
        try:
            job.ats_threshold = float(threshold)
        except (TypeError, ValueError):
            pass  # ignore invalid input

        # ✅ Checkbox handling
        job.threshold_enabled = True if enabled == "on" else False

        job.save()

    return redirect("view_applicants", job_id=job.id)

@login_required
def view_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    applications = Application.objects.filter(job=job).select_related('candidate')

    # 🔥 Filter strictly based on ATS threshold
    if job.threshold_enabled and job.ats_threshold is not None:
        applications = applications.filter(score__isnull=False, score__gte=job.ats_threshold)

    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)

    # 🔥 Sort by score (top candidates first)
    applications = applications.order_by('-score', '-created_at')

    return render(request, 'applications/applicants.html', {
        'job': job,
        'applications': applications
    })