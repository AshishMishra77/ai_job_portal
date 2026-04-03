from django.shortcuts import render
from services.parser import extract_text
from services.ollama_client import generate_feedback
from services.matcher import compute_score

def analyze_resume(request):
    if request.method == 'POST':
        resume = request.FILES['resume']
        job_desc = request.POST.get('job_desc')

        text = extract_text(resume)
        score = compute_score(text, job_desc)
        feedback = generate_feedback(text, job_desc)

        return render(request, 'ai/result.html', {
            'score': score,
            'feedback': feedback
        })

    return render(request, 'ai/upload.html')
