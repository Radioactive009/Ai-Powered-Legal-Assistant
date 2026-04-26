import json
import time
import sys
import os
import requests

# Add parent directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator.pipeline import run_debate
from agents.pro_agent import generate_pro_argument
from agents.con_agent import generate_con_argument

def get_ollama_response(prompt, model="phi3"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model, "prompt": prompt, "stream": False,
                "options": {"num_predict": 300}
            },
            timeout=60
        )
        return response.json().get("response", "")
    except Exception as e:
        return f"Error: {e}"

# --- NEW ACADEMIC METRICS ---

def calculate_structure_score(output, method):
    """
    +1 per arg, +1 if reason exists, +1 if impact exists.
    """
    if method == "raw":
        # Raw LLM usually gives one long response, treat as 1 arg with potential reason
        return 1.2 # Baseline structure
    
    # For Prompt and Hybrid, iterate through the structured list
    args = []
    if method == "prompt":
        args = output.get("pro", []) + output.get("con", [])
    elif method == "hybrid":
        args = output.get("pro", []) + output.get("con", [])
        
    if not args: return 0
    
    total_score = 0
    for arg in args:
        score = 1 # Argument detected
        if len(arg.get("reason", "")) > 0: score += 1
        if len(arg.get("impact", "")) > 0: score += 1
        total_score += score
    
    return round(total_score / len(args), 2)

def calculate_reasoning_score(output, method):
    """
    Keyword count + length heuristics (> 8 words).
    """
    keywords = ["because", "therefore", "leads to", "results in"]
    
    if method == "raw":
        text = output.get("text", "").lower()
        kw_count = sum(text.count(k) for k in keywords)
        length_bonus = 1 if len(text.split()) > 20 else 0
        return round(kw_count + length_bonus, 2)

    args = output.get("pro", []) + output.get("con", []) if method == "prompt" else output.get("pro", []) + output.get("con", [])
    
    total_reasoning = 0
    for arg in args:
        text = (arg.get("point", "") + " " + arg.get("reason", "") + " " + arg.get("impact", "")).lower()
        kw_count = sum(text.count(k) for k in keywords)
        
        len_score = 0
        if len(arg.get("reason", "").split()) > 8: len_score += 1
        if len(arg.get("impact", "").split()) > 8: len_score += 1
        
        total_reasoning += (kw_count + len_score)
        
    return round(total_reasoning / (len(args) if args else 1), 2)

# --- BASELINE FUNCTIONS ---

def raw_llm_baseline(question):
    response = get_ollama_response(f"Answer this question with reasoning: {question}")
    out = {"text": response}
    return {
        "output": out,
        "metrics": {
            "structure": calculate_structure_score(out, "raw"),
            "reasoning": calculate_reasoning_score(out, "raw"),
            "decision": 0
        }
    }

def prompt_engineered_baseline(question):
    pro = generate_pro_argument(question)
    con = generate_con_argument(question)
    out = {"pro": pro, "con": con}
    return {
        "output": out,
        "metrics": {
            "structure": calculate_structure_score(out, "prompt"),
            "reasoning": calculate_reasoning_score(out, "prompt"),
            "decision": 0
        }
    }

def hybrid_system_baseline(question):
    res = run_debate(question)
    return {
        "output": res,
        "metrics": {
            "structure": calculate_structure_score(res, "hybrid"),
            "reasoning": calculate_reasoning_score(res, "hybrid"),
            "decision": 1
        }
    }

def run_evaluation():
    questions = [
        "Is AI dangerous?", "Should college be free?", "Is remote work better?",
        "Should cryptocurrencies be regulated?", "Is nuclear energy the future?"
    ]
    results = []
    for q in questions:
        print(f"Evaluating: {q}")
        results.append({
            "question": q,
            "raw": raw_llm_baseline(q),
            "prompt": prompt_engineered_baseline(q),
            "hybrid": hybrid_system_baseline(q)
        })
    
    with open(os.path.join("evaluation", "results_v2.json"), 'w') as f:
        json.dump(results, f, indent=4)
    print("Evaluation complete. Saved to results_v2.json")

if __name__ == "__main__":
    run_evaluation()
