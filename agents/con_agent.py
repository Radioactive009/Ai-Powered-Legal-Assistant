import requests

def generate_con_argument(question):
    prompt = f"""
Give arguments AGAINST the statement below.

Question: {question}

Rules:
* Give EXACTLY 2 arguments
* Each argument must be 1-2 lines only
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
            
        # Clean output: strip whitespace and take only the response content
        return data["response"].strip()
    except Exception as e:
        return f"Agent Error: {str(e)}"