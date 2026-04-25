from concurrent.futures import ThreadPoolExecutor
from agents.pro_agent import generate_pro_argument
from agents.con_agent import generate_con_argument
from judge.rule_judge import rule_based_judge
from judge.llm_judge import llm_tiebreaker

def run_debate(question):
    """
    Hybrid pipeline: Uses rule-based scoring first, with an LLM tie-breaker if scores are equal.
    """
    with ThreadPoolExecutor() as executor:
        future_pro = executor.submit(generate_pro_argument, question)
        future_con = executor.submit(generate_con_argument, question)
        
        pro_output = future_pro.result()
        con_output = future_con.result()

    # 1. Primary Rule-Based Judge
    rule_res = rule_based_judge(pro_output, con_output)
    pro_score = rule_res["scores"]["pro"]
    con_score = rule_res["scores"]["con"]

    # 2. Tie-Breaker Condition (Difference < 0.05)
    if abs(pro_score - con_score) < 0.05:
        winner = llm_tiebreaker(question, pro_output, con_output)
        decision_type = "llm_tiebreaker"
        reason = f"Decision made by AI tie-breaker based on logical depth (Original scores: Pro {pro_score} vs Con {con_score})"
    else:
        winner = rule_res["winner"]
        decision_type = "rule_based"
        reason = rule_res["reason"]

    return {
        "question": question,
        "pro": pro_output,
        "con": con_output,
        "result": {
            "winner": winner,
            "scores": {
                "pro": pro_score,
                "con": con_score
            },
            "confidence": max(pro_score, con_score),
            "decision_type": decision_type,
            "reason": reason
        }
    }