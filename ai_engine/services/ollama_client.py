import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def query_ollama(prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    })

    return response.json()['response']


def generate_feedback(resume_text, job_desc):
    prompt = f"""
    Compare this resume with job description.

    Resume:
    {resume_text[:2000]}

    Job:
    {job_desc[:1000]}

    Give:
    - Match summary
    - Missing skills
    - Suggestions
    """

    return query_ollama(prompt)