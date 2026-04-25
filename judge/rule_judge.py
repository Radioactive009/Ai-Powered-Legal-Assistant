def rule_based_judge(pro_data, con_data):
    """
    Scoring-based judge that handles structured JSON data.
    """
    keywords = ["because", "therefore", "leads to", "results in"]
    
    # Helper to convert list of dicts to a searchable string
    def get_full_text(data):
        text = ""
        for item in data:
            text += f" {item.get('point', '')} {item.get('reason', '')} {item.get('impact', '')}"
        return text.lower()

    pro_text = get_full_text(pro_data)
    con_text = get_full_text(con_data)
    
    pro_score = sum(pro_text.count(k) for k in keywords)
    con_score = sum(con_text.count(k) for k in keywords)

    if pro_score > con_score:
        winner = "Pro"
        reason = f"Pro arguments had stronger logical depth (Score: {pro_score} vs {con_score})."
    elif con_score > pro_score:
        winner = "Con"
        reason = f"Con arguments had stronger logical depth (Score: {con_score} vs {pro_score})."
    else:
        winner = "Tie"
        reason = f"Both sides provided equal logical reasoning (Score: {pro_score})."

    return f"Winner: {winner}\nReason: {reason}"
