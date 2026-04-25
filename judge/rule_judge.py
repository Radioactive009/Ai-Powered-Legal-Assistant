def rule_based_judge(pro, con):
    """
    Simple rule-based judge that compares response lengths.
    """
    pro_len = len(pro)
    con_len = len(con)

    if pro_len > con_len:
        winner = "Pro"
        reason = f"Pro provided a more detailed response ({pro_len} characters vs {con_len} characters)."
    elif con_len > pro_len:
        winner = "Con"
        reason = f"Con provided a more detailed response ({con_len} characters vs {pro_len} characters)."
    else:
        winner = "Tie"
        reason = "Both sides provided arguments of equal length."

    return f"Winner: {winner}\nReason: {reason}"
