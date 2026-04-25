import requests

def generate_pro_argument(question):
    prompt = f"""
Give arguments IN FAVOR of the statement below.

Question: {question}

Rules:
* Give EXACTLY 2 arguments
* Each argument must be 1-2 lines only
* Use logical connectors like 'because', 'therefore', 'leads to', or 'results in' to strengthen your points.
* Be direct and logical
* No storytelling
* No extra explanation

Output format:
1. <argument>
2. <argument>
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 120
                }
            },
            timeout=300
        )
        response.raise_for_status()
        data = response.json()
        
        if "response" not in data:
            return f"Error: Ollama returned an unexpected format: {data.get('error', 'Unknown error')}"
            
        return data["response"].strip()
    except Exception as e:
        return f"Agent Error: {str(e)}"