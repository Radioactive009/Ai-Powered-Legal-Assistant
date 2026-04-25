def rule_based_judge(pro, con):
    """
    Scoring-based judge that counts logical connectors.
    """
    keywords = ["because", "therefore", "leads to", "results in"]
    
    pro_lower = pro.lower()
    con_lower = con.lower()
    
    pro_score = sum(pro_lower.count(k) for k in keywords)
    con_score = sum(con_lower.count(k) for k in keywords)

    if pro_score > con_score:
        winner = "Pro"
        reason = f"Pro arguments were more logical (Score: {pro_score} vs {con_score})."
    elif con_score > pro_score:
        winner = "Con"
        reason = f"Con arguments were more logical (Score: {con_score} vs {pro_score})."
    else:
        winner = "Tie"
        reason = f"Both sides had equal logical strength (Score: {pro_score})."

    return f"Winner: {winner}\nReason: {reason}"
