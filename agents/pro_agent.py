import requests

def generate_pro_argument(question):
    prompt = f"Provide 2 short, concise arguments IN FAVOR of: {question}. Keep it very brief."

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:latest",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 150
                }
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        if "response" not in data:
            return f"Error: Ollama returned an unexpected format: {data.get('error', 'Unknown error')}"
            
        return data["response"]
    except Exception as e:
        return f"Agent Error: {str(e)}"