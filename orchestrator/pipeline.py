from concurrent.futures import ThreadPoolExecutor
from agents.pro_agent import generate_pro_argument
from agents.con_agent import generate_con_argument
from judge.llm_judge import judge_arguments

def run_debate(question):
    with ThreadPoolExecutor() as executor:
        future_pro = executor.submit(generate_pro_argument, question)
        future_con = executor.submit(generate_con_argument, question)
        
        pro = future_pro.result()
        con = future_con.result()

    result = judge_arguments(question, pro, con)

    return {
        "question": question,
        "pro": pro,
        "con": con,
        "result": result
    }