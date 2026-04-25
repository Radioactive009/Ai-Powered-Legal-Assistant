import requests

def llm_tiebreaker(question, pro_args, con_args):
    """
    Lightweight LLM call to break ties between structurally equal arguments.
    """
    prompt = f"""
Question: {question}

Pro Arguments:
{pro_args}

Con Arguments:
{con_args}

Both sides are structurally strong. 

Which side is more logically sound?

Answer ONLY one word:
Pro or Con
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 20
                }
            },
            timeout=30
        )
        response.raise_for_status()
        winner = response.json().get("response", "").strip().capitalize()
        
        # Ensure we only return Pro or Con
        if "Pro" in winner:
            return "Pro"
        elif "Con" in winner:
            return "Con"
        return "Tie" # Fallback if model fails to be decisive
    except Exception:
        return "Tie"