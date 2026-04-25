import requests

def judge_arguments(question, pro, con):
    prompt = f"""
    You are an unbiased judge.

    Question: {question}

    PRO:
    {pro}

    CON:
    {con}

    Decide:
    - Which side is stronger (Pro or Con)
    - Explain why
    - Give confidence (0-100)

    Output format:
    Winner:
    Reason:
    Confidence:
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