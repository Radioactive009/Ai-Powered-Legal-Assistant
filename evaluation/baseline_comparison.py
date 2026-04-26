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
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 300}
            },
            timeout=60
        )
        return response.json().get("response", "")
    except Exception as e:
        return f"Error: {e}"

def count_keywords(text):
    keywords = ["because", "leads to", "results in", "therefore"]
    text = text.lower()
    return sum(text.count(k) for k in keywords)

def raw_llm_baseline(question):
    prompt = f"Answer this question with reasoning: {question}"
    response = get_ollama_response(prompt)
    return {
        "text": response,
        "metrics": {
            "length": len(response.split()),
            "args_count": 1, # Unified response
            "keywords": count_keywords(response),
            "has_decision": False
        }
    }

def prompt_engineered_baseline(question):
    # Call agents directly without the judge
    pro_args = generate_pro_argument(question)
    con_args = generate_con_argument(question)
    
    full_text = str(pro_args) + " " + str(con_args)
    return {
        "pro": pro_args,
        "con": con_args,
        "metrics": {
            "length": len(full_text.split()),
            "args_count": len(pro_args) + len(con_args),
            "keywords": count_keywords(full_text),
            "has_decision": False
        }
    }

def hybrid_system_baseline(question):
    result = run_debate(question)
    full_text = str(result["pro"]) + " " + str(result["con"]) + " " + str(result["result"])
    return {
        "full_output": result,
        "metrics": {
            "length": len(full_text.split()),
            "args_count": len(result["pro"]) + len(result["con"]),
            "keywords": count_keywords(full_text),
            "has_decision": True
        }
    }

def run_comparison():
    questions = [
        "Is AI dangerous to humanity?",
        "Should college be free for everyone?",
        "Is remote work better than office work?",
        "Should cryptocurrencies be regulated?",
        "Is nuclear energy the future of green power?",
        "Should social media algorithms be public?",
        "Is animal testing ethical for medical research?",
        "Should coding be a mandatory subject in school?",
        "Is capitalism the best economic system?",
        "Should the minimum wage be increased?",
        "Is a 4-day work week productive?",
        "Should everyone live in cities?",
        "Is social media making us more lonely?",
        "Should we strive for a minimalist lifestyle?",
        "Is gaming a productive hobby?",
        "Should mental health days be mandatory?",
        "Is space exploration worth the cost?",
        "Should CEOs have a salary cap?",
        "Is a vegan diet better for the environment?",
        "Should standard testing be abolished?"
    ]

    all_results = []
    
    print(f"Starting baseline comparison for {len(questions)} questions...")

    for i, q in enumerate(questions):
        print(f"Evaluating ({i+1}/{len(questions)}): {q}")
        
        raw = raw_llm_baseline(q)
        prompt_eng = prompt_engineered_baseline(q)
        hybrid = hybrid_system_baseline(q)
        
        all_results.append({
            "question": q,
            "raw_llm": raw,
            "prompt_engineered": prompt_eng,
            "hybrid": hybrid
        })
        time.sleep(1)

    # Save results
    output_path = os.path.join(os.path.dirname(__file__), 'results.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=4)

    # Print Summary
    print("\n" + "="*30)
    print("EVALUATION SUMMARY")
    print("="*30)
    
    methods = ["raw_llm", "prompt_engineered", "hybrid"]
    for m in methods:
        avg_len = sum(r[m]["metrics"]["length"] for r in all_results) / len(all_results)
        avg_kw = sum(r[m]["metrics"]["keywords"] for r in all_results) / len(all_results)
        dec_rate = (sum(1 for r in all_results if r[m]["metrics"]["has_decision"]) / len(all_results)) * 100
        
        print(f"\nMethod: {m.upper()}")
        print(f" - Avg Response Length: {avg_len:.1f} words")
        print(f" - Avg Keyword Count: {avg_kw:.1f}")
        print(f" - Decision Output Rate: {dec_rate:.0f}%")

    print("\nComparison complete. Detailed results saved to results.json.")

if __name__ == "__main__":
    run_comparison()
