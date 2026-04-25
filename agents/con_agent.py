import requests

def generate_con_argument(question):
    prompt = f"Provide 2 short, concise arguments AGAINST: {question}. Keep it very brief."

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3:8b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 150
            }
        }
    )

    return response.json()["response"]