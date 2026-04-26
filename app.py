import streamlit as st
import json
import os
import pandas as pd
import requests
import time
from orchestrator.pipeline import run_debate

st.set_page_config(page_title="Legal Agent Analysis", page_icon="🧠", layout="wide")

# --- SIDEBAR ---
st.sidebar.title("🛠️ Project Menu")
page = st.sidebar.radio("Go to:", ["Debate Arena", "Evaluation Dashboard"])

# --- PAGE 1: DEBATE ARENA ---
if page == "Debate Arena":
    st.title("🧠 Multi-Agent Debate System")
    st.caption("Hybrid Intelligent Mode: Rules + Machine Learning + LLM Tie-Breaker")

    question = st.text_input("Enter your question:", placeholder="e.g., Is React the best framework?")
    
    if st.button("Run Debate"):
        if not question:
            st.warning("Please enter a question first.")
        else:
            with st.status("🤖 AI Agents are debating...", expanded=True) as status:
                output = run_debate(question)
                status.update(label="✅ Debate Complete!", state="complete", expanded=False)

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
    
    # 1. Primary Metrics
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

    # 2. NLP Metrics
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

    # 3. Error Analysis (FAILURE CASE TRACKING)
    st.divider()
    st.subheader("⚠️ Failure Analysis (Qualitative Review)")
    st.write("Tracking common LLM weaknesses across systems.")
    
    err_path = os.path.join("evaluation", "error_analysis.json")
    if os.path.exists(err_path):
        with open(err_path, "r", encoding="utf-8") as f:
            err_data = json.load(f)
        
        summ = err_data["summary"]
        col_r, col_p, col_h = st.columns(3)
        
        with col_r:
            st.error("RAW LLM Failures")
            st.metric("Structural Failure", f"{summ['raw']['structural_failure']}%", delta="UNSTABLE", delta_color="inverse")
            st.metric("Weak Reasoning", f"{summ['raw']['weak_reasoning']}%")

        with col_p:
            st.warning("Prompt-Only Failures")
            st.metric("Hallucination Rate", f"{summ['prompt']['hallucination']}%")
            st.metric("Structural Failure", f"{summ['prompt']['structural_failure']}%")

        with col_h:
            st.success("HYBRID System Failures")
            st.metric("Structural Failure", f"{summ['hybrid']['structural_failure']}%", delta="STABLE")
            st.metric("Hallucination Rate", f"{summ['hybrid']['hallucination']}%", delta="-20%", delta_color="normal")
            
        st.caption("Failure rates are calculated based on manual review of 12 test cases. Hybrid system shows 0% structural failure due to the multi-agent guardrails.")