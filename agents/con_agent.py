import requests

def generate_con_argument(question):
    prompt = f"""
    You are a critical thinker.

    Generate strong arguments AGAINST the following:

    {question}

    Give 3 points with reasoning.
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]