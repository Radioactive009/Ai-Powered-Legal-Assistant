from concurrent.futures import ThreadPoolExecutor
from agents.pro_agent import generate_pro_argument
from agents.con_agent import generate_con_argument
from judge.llm_judge import judge_arguments

def run_debate(question):
    """
    Parallelized pipeline using LLM-based judging for smart decision making.
    """
    with ThreadPoolExecutor() as executor:
        future_pro = executor.submit(generate_pro_argument, question)
        future_con = executor.submit(generate_con_argument, question)
        
        pro_output = future_pro.result()
        con_output = future_con.result()

    # Advanced LLM Judge
    final_decision = judge_arguments(question, pro_output, con_output)

    return {
        "question": question,
        "pro": pro_output,
        "con": con_output,
        "result": final_decision
    }