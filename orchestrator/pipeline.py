from concurrent.futures import ThreadPoolExecutor
from agents.pro_agent import generate_pro_argument
from agents.con_agent import generate_con_argument
from judge.rule_judge import rule_based_judge

def run_debate(question):
    """
    Fast, deterministic pipeline with rule-based scoring and structured results.
    """
    with ThreadPoolExecutor() as executor:
        future_pro = executor.submit(generate_pro_argument, question)
        future_con = executor.submit(generate_con_argument, question)
        
        pro_output = future_pro.result()
        con_output = future_con.result()

    # Rule-Based Judge (Deterministic and fast)
    structured_decision = rule_based_judge(pro_output, con_output)

    return {
        "question": question,
        "pro": pro_output,
        "con": con_output,
        "result": structured_decision
    }