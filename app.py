import streamlit as st
import json
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from orchestrator.pipeline import run_debate
from evaluation.baseline_comparison import raw_llm_baseline, prompt_engineered_baseline

st.set_page_config(page_title="Legal Agent Analysis", page_icon="🧠", layout="wide")

# --- UTILS ---
def get_metrics_for_text(pro_args, con_args, res):
    """Calculates academic scores for a set of arguments."""
    all_args = pro_args + con_args
    # 1. Structure
    struct = 0
    for a in all_args:
        if a.get("point") and a.get("reason") and a.get("impact"): struct += 1
    avg_struct = (struct / len(all_args) * 4) if all_args else 0
    
    # 2. Reasoning
    reasoning = 0
    keywords = ["because", "therefore", "leads to", "results in", "since", "due to", "indicating", "essential", "risks"]
    for a in all_args:
        text = f"{a.get('reason','')} {a.get('impact','')}".lower()
        reasoning += sum(1 for k in keywords if k in text)
    avg_reason = (reasoning / len(all_args) * 4) if all_args else 0
    
    # 3. Decision
    dec = 100 if res.get("winner") != "Draw" else 0
    
    return {"Structure": avg_struct, "Reasoning": avg_reason, "Decision": dec}

# --- SIDEBAR ---
st.sidebar.title("🛠️ Project Menu")
page = st.sidebar.radio("Go to:", ["Debate Arena", "Evaluation Dashboard"])
live_compare = st.sidebar.checkbox("🚀 Live Comparison Mode (Runs 3 Models)", value=False)

# --- PAGE 1: DEBATE ARENA ---
if page == "Debate Arena":
    st.title("🧠 Multi-Agent Debate System")
    st.caption("Hybrid Intelligent Mode: Rules + Machine Learning + LLM Tie-Breaker")

    question = st.text_input("Enter your question:", placeholder="e.g., Is AI better than humans?")
    
    if st.button("Run Debate"):
        if not question:
            st.warning("Please enter a question first.")
        else:
            with st.status("🤖 Running models...", expanded=True) as status:
                if live_compare:
                    status.update(label="⌛ Running Live Comparison (Raw vs Prompt vs Hybrid)...")
                    with ThreadPoolExecutor() as executor:
                        f_hybrid = executor.submit(run_debate, question)
                        f_raw = executor.submit(raw_llm_baseline, question)
                        f_prompt = executor.submit(prompt_engineered_baseline, question)
                        
                        hybrid_out = f_hybrid.result()
                        raw_out = f_raw.result()
                        prompt_out = f_prompt.result()
                    
                    # Calculate metrics for all 3
                    m_h = get_metrics_for_text(hybrid_out["pro"], hybrid_out["con"], hybrid_out["result"])
                    m_r = get_metrics_for_text(raw_out["pro"], raw_out["con"], raw_out["result"])
                    m_p = get_metrics_for_text(prompt_out["pro"], prompt_out["con"], prompt_out["result"])
                    
                    comparison_df = pd.DataFrame([
                        {"Method": "RAW", "Structure": m_r["Structure"], "Reasoning": m_r["Reasoning"], "Decision": m_r["Decision"]},
                        {"Method": "PROMPT", "Structure": m_p["Structure"], "Reasoning": m_p["Reasoning"], "Decision": m_p["Decision"]},
                        {"Method": "HYBRID", "Structure": m_h["Structure"], "Reasoning": m_h["Reasoning"], "Decision": m_h["Decision"]},
                    ])
                    output = hybrid_out # Main display is still Hybrid
                else:
                    output = run_debate(question)
                    m_h = get_metrics_for_text(output["pro"], output["con"], output["result"])
                    comparison_df = pd.DataFrame([{"Method": "HYBRID", "Structure": m_h["Structure"], "Reasoning": m_h["Reasoning"], "Decision": m_h["Decision"]}])
                
                status.update(label="✅ Analysis Complete!", state="complete", expanded=False)

            # --- DISPLAY GRAPHS ---
            st.subheader("📊 Live Comparison Analysis")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.caption("🏗️ Structure Score")
                st.bar_chart(comparison_df.set_index("Method")["Structure"])
            with c2:
                st.caption("🧠 Reasoning Score")
                st.bar_chart(comparison_df.set_index("Method")["Reasoning"])
            with c3:
                st.caption("🎯 Decision Rate (%)")
                st.bar_chart(comparison_df.set_index("Method")["Decision"])

            st.divider()
            # ... Rest of the display (Pro/Con args) ...
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📌 Pro Arguments")
                for i, arg in enumerate(output["pro"]):
                    with st.container(border=True):
                        st.markdown(f"**{i+1}. {arg.get('point')}**")
                        st.write(f"💡 *Reason:* {arg.get('reason')}")
            with col2:
                st.subheader("📌 Con Arguments")
                for i, arg in enumerate(output["con"]):
                    with st.container(border=True):
                        st.markdown(f"**{i+1}. {arg.get('point')}**")
                        st.write(f"💡 *Reason:* {arg.get('reason')}")
            
            st.divider()
            res = output["result"]
            with st.container(border=True):
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("Winner", res["winner"])
                col_b.metric("Pro Score", res["scores"]["pro"])
                col_c.metric("Con Score", res["scores"]["con"])
                col_d.metric("ML Pick", res["ml_prediction"])
                st.write(f"**Reason:** {res['reason']}")
                st.caption(f"Decision Method: {res['decision_type'].replace('_', ' ').title()} | Confidence: {res['confidence']*100}%")

# --- PAGE 2: EVALUATION DASHBOARD ---
elif page == "Evaluation Dashboard":
    st.title("📊 Academic Evaluation Dashboard")
    # (Same as before, showing the 20-sample aggregates)
    results_path = os.path.join("evaluation", "results_v2.json")
    if os.path.exists(results_path):
        with open(results_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        methods = ["raw", "prompt", "hybrid"]
        metrics_list = []
        for m in methods:
            avg_struct = sum(r[m]["metrics"]["structure"] for r in data) / len(data)
            avg_reason = sum(r[m]["metrics"]["reasoning"] for r in data) / len(data)
            dec_rate = (sum(r[m]["metrics"]["decision"] for r in data) / len(data)) * 100
            metrics_list.append({"Method": m.upper(), "Structure": avg_struct, "Reasoning": avg_reason, "Decision (%)": dec_rate})
        df = pd.DataFrame(metrics_list)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("🏗️ Structure Score")
            st.bar_chart(df.set_index("Method")["Structure"])
        with col2:
            st.subheader("🧠 Reasoning Score")
            st.bar_chart(df.set_index("Method")["Reasoning"])
        with col3:
            st.subheader("🎯 Decision Rate")
            st.bar_chart(df.set_index("Method")["Decision (%)"])
    
    # NLP and Error Analysis sections...
    st.divider()
    st.subheader("🔤 NLP Quality Analysis (BLEU & ROUGE)")
    st.write("Compared to baseline, hybrid outputs show **higher content coverage and structural completeness**.")
    nlp_path = os.path.join("evaluation", "bleu_rouge_results.json")
    if os.path.exists(nlp_path):
        with open(nlp_path, "r", encoding="utf-8") as f:
            nlp_data = json.load(f); summary = nlp_data["summary"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("BLEU Score", summary["avg_bleu"])
        c2.metric("ROUGE-1", summary["avg_rouge1"])
        c3.metric("ROUGE-2", summary["avg_rouge2"])
        c4.metric("ROUGE-L", summary["avg_rougeL"])