from concurrent.futures import ThreadPoolExecutor
from agents.pro_agent import generate_pro_argument
from agents.con_agent import generate_con_argument
from judge.rule_judge import rule_based_judge

def run_debate(question):
    """
    Parallelized pipeline for faster local execution with high timeout support.
    """
    with ThreadPoolExecutor() as executor:
        future_pro = executor.submit(generate_pro_argument, question)
        future_con = executor.submit(generate_con_argument, question)
        
        pro_output = future_pro.result()
        con_output = future_con.result()

    # Simple Rule-Based Judge
    simple_judge_result = rule_based_judge(pro_output, con_output)

    return {
        "question": question,
        "pro": pro_output,
        "con": con_output,
        "result": simple_judge_result
    }