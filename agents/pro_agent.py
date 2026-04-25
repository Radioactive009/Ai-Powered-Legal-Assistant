import requests

def generate_pro_argument(question):
    prompt = f"""
    You are a debate expert.

    Generate strong arguments IN FAVOR of the following:

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