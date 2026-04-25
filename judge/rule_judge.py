def rule_based_judge(pro_data, con_data):
    """
    Structured hybrid judge using deterministic scoring rules.
    """
    def score_side(data):
        total_score = 0
        keywords = ["because", "leads to", "results in"]
        
        for arg in data:
            arg_score = 0
            
            # 1. Keyword check
            reason_text = arg.get('reason', '').lower()
            impact_text = arg.get('impact', '').lower()
            full_text = reason_text + " " + impact_text
            
            if any(k in full_text for k in keywords):
                arg_score += 1
                
            # 2. Reason length check (> 8 words)
            if len(reason_text.split()) > 8:
                arg_score += 1
                
            # 3. Impact length check (> 8 words)
            if len(impact_text.split()) > 8:
                arg_score += 1
            
            total_score += arg_score
            
        return total_score

    pro_score_raw = score_side(pro_data)
    con_score_raw = score_side(con_data)

    # Normalize scores between 0 and 1 (Max possible score is 6 for 2 arguments)
    pro_norm = round(pro_score_raw / 6.0, 2)
    con_norm = round(con_score_raw / 6.0, 2)

    if pro_score_raw > con_score_raw:
        winner = "Pro"
        confidence = pro_norm
        reason = f"Pro arguments demonstrated higher structural complexity and logical depth."
    elif con_score_raw > pro_score_raw:
        winner = "Con"
        confidence = con_norm
        reason = f"Con arguments demonstrated higher structural complexity and logical depth."
    else:
        winner = "Tie"
        confidence = pro_norm
        reason = "Both sides provided arguments of equal structural and logical quality."

    return {
        "winner": winner,
        "scores": {
            "pro": pro_norm,
            "con": con_norm
        },
        "confidence": confidence,
        "reason": reason
    }
