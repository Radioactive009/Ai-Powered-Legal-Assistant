from agents.pro_agent import generate_pro_argument
from agents.con_agent import generate_con_argument
from judge.rule_judge import rule_based_judge

def run_debate(question):
    """
    Optimized pipeline with sequential calls and rule-based judging.
    """
    # 1. Generate Pro
    pro_output = generate_pro_argument(question)

    # 2. Generate Con
    con_output = generate_con_argument(question)

    # 3. Simple Rule-Based Judge
    simple_judge_result = rule_based_judge(pro_output, con_output)

    return {
        "question": question,
        "pro": pro_output,
        "con": con_output,
        "result": simple_judge_result
    }