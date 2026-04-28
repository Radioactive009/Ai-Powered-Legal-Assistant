import requests
import json
import re

def generate_con_argument(question, context=None):
    context_str = f"\n\nUse the following historical context if relevant:\n{context}" if context else ""
    prompt = f"""
Give arguments AGAINST the statement below.{context_str}

Question: {question}

Rules:
* Generate EXACTLY 2 arguments
* Each argument must include:
  * point (main idea)
  * reason (why it is valid)
  * impact (real-world effect)
* Keep each field concise (1 line)

Output format (STRICT JSON):
[
  {{
    "point": "...",
    "reason": "...",
    "impact": "..."
  }},
  {{
    "point": "...",
    "reason": "...",
    "impact": "..."
  }}
]
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 300  # Increased for JSON overhead
                }
            },
            timeout=300
        )
        response.raise_for_status()
        raw_output = response.json().get("response", "").strip()
        
        # Clean potential markdown code blocks
        json_str = re.sub(r'```json|```', '', raw_output).strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return [{"point": "Parsing Error", "reason": "AI failed to return valid JSON", "impact": "N/A"}]
            
    except Exception as e:
        return [{"point": "Agent Error", "reason": str(e), "impact": "N/A"}]