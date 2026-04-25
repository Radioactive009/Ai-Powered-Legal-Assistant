import requests
import json

def judge_arguments(question, pro_data, con_data):
    """
    Advanced LLM-based judge that analyzes structured data to pick a winner.
    """
    # Format the structured data for the judge
    def format_args(data):
        formatted = ""
        for i, item in enumerate(data):
            formatted += f"\nArgument {i+1}:\n- Point: {item.get('point')}\n- Reason: {item.get('reason')}\n- Impact: {item.get('impact')}\n"
        return formatted

    pro_formatted = format_args(pro_data)
    con_formatted = format_args(con_data)

    prompt = f"""
You are a master debate judge. Your goal is to analyze the following debate and pick a CLEAR winner. 

Question: {question}

PRO ARGUMENTS:
{pro_formatted}

CON ARGUMENTS:
{con_formatted}

CRITERIA:
1. Logical consistency: Does the reason support the point?
2. Real-world impact: Which side presents more significant consequences?
3. Depth: Which side has more nuanced reasoning?

INSTRUCTIONS:
- You MUST pick a winner (either PRO or CON). Do not call it a tie.
- Provide "Smart Reasoning" that specifically mentions the points raised.
- Be decisive.

Output format:
Winner: [PRO or CON]
Reason: [Your smart, analytical reasoning here]
Confidence: [0-100]
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 300
                }
            },
            timeout=300
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"Judge Error: {str(e)}"