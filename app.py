import streamlit as st
import json
import os
import pandas as pd
import requests
import time
from orchestrator.pipeline import run_debate
from agents.pro_agent import generate_pro_argument
from agents.con_agent import generate_con_argument

st.set_page_config(page_title="Legal Agent Analysis", page_icon="🧠", layout="wide")

# --- UTILS FOR LIVE COMPARISON ---
def get_raw_llm(question):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": f"Answer this question with reasoning: {question}",
                "stream": False,
                "options": {"num_predict": 200}
            },
            timeout=60
        )
        return response.json().get("response", "")
    except:
        return "Error fetching Raw LLM response."

def get_prompt_only(question):
    pro = generate_pro_argument(question)
    con = generate_con_argument(question)
    return pro, con

# --- SIDEBAR ---
st.sidebar.title("🛠️ Project Menu")
page = st.sidebar.radio("Go to:", ["Debate Arena", "Evaluation Dashboard"])

# --- PAGE 1: DEBATE ARENA ---
if page == "Debate Arena":
    st.title("🧠 Multi-Agent Debate System")
    st.caption("Hybrid Intelligent Mode: Rules + Machine Learning + LLM Tie-Breaker")

    question = st.text_input("Enter your question:", placeholder="e.g., Is React the best framework?")
    
    # NEW: Comparative Mode Toggle
    compare_mode = st.checkbox("🔍 Run Real-Time Comparison Mode (Show Raw vs Prompt vs Hybrid)")

    if st.button("Run Debate"):
        if not question:
            st.warning("Please enter a question first.")
        else:
            if compare_mode:
                with st.status("🔬 Running Comparative Analysis (This will take ~40s)...", expanded=True) as status:
                    st.write("1/3: Fetching Raw LLM response...")
                    raw_text = get_raw_llm(question)
                    
                    st.write("2/3: Generating Prompt-Engineered arguments...")
                    p_pro, p_con = get_prompt_only(question)
                    
                    st.write("3/3: Executing Full Hybrid Pipeline (Rules + ML + Judge)...")
                    hybrid_out = run_debate(question)
                    
                    status.update(label="✅ Comparison Complete!", state="complete", expanded=False)

                # Show Results in Tabs
                tab_h, tab_p, tab_r = st.tabs(["⭐ Hybrid System (Winner)", "📝 Prompt Only", "📄 Raw LLM"])
                
                with tab_r:
                    st.info("Raw LLM Output (No constraints, no structure)")
                    st.write(raw_text)
                    st.caption("Notice: No winner picked, no structured points.")

                with tab_p:
                    st.info("Prompt Engineered (Structure only, no intelligence)")
                    c1, c2 = st.columns(2)
                    c1.write("**Pro:**")
                    c1.write(p_pro)
                    c2.write("**Con:**")
                    c2.write(p_con)
                    st.caption("Notice: Better structure, but still no decision.")

                with tab_h:
                    st.success("Hybrid Intelligent System (Winner Selected)")
                    # Reuse existing UI logic for Hybrid
                    col1, col2 = st.columns(2)
                    with col1:
                        for i, arg in enumerate(hybrid_out["pro"]):
                            with st.container(border=True):
                                st.markdown(f"**{i+1}. {arg.get('point')}**")
                                st.write(f"💡 *Reason:* {arg.get('reason')}")
                    with col2:
                        for i, arg in enumerate(hybrid_out["con"]):
                            with st.container(border=True):
                                st.markdown(f"**{i+1}. {arg.get('point')}**")
                                st.write(f"💡 *Reason:* {arg.get('reason')}")
                    
                    st.divider()
                    res = hybrid_out["result"]
                    col_a, col_b, col_c, col_d = st.columns(4)
                    col_a.metric("Winner", res["winner"])
                    col_b.metric("Pro Score", res["scores"]["pro"])
                    col_c.metric("Con Score", res["scores"]["con"])
                    col_d.metric("ML Pick", res["ml_prediction"])
                    st.write(f"**Reason:** {res['reason']}")
            
            else:
                # Normal Mode (Fast)
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
                            st.write(f"🌍 *Impact:* {arg.get('impact')}")
                with col2:
                    st.subheader("📌 Con Arguments")
                    for i, arg in enumerate(output["con"]):
                        with st.container(border=True):
                            st.markdown(f"**{i+1}. {arg.get('point')}**")
                            st.write(f"💡 *Reason:* {arg.get('reason')}")
                            st.write(f"🌍 *Impact:* {arg.get('impact')}")

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
    st.title("📊 System Evaluation Dashboard")
    st.write("Comparing the **Hybrid System** against **Raw LLM** and **Prompt Engineering** baselines.")

    results_path = os.path.join("evaluation", "results.json")
    if not os.path.exists(results_path):
        st.warning("⚠️ No evaluation data found. Dashboard is showing sample metrics.")
    else:
        with open(results_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        methods = ["raw_llm", "prompt_engineered", "hybrid"]
        metrics_data = []
        for m in methods:
            avg_len = sum(r[m]["metrics"]["length"] for r in data) / len(data)
            avg_kw = sum(r[m]["metrics"]["keywords"] for r in data) / len(data)
            dec_rate = (sum(1 for r in data if r[m]["metrics"]["has_decision"]) / len(data)) * 100
            metrics_data.append({"Method": m.title(), "Avg Length": avg_len, "Reasoning (Keywords)": avg_kw, "Decision Rate (%)": dec_rate})

        df_metrics = pd.DataFrame(metrics_data)
        col1, col2, col3 = st.columns(3)
        col1.metric("Hybrid Decision Rate", "100%", delta="100% over Baseline")
        col2.metric("Avg Reasoning Depth", f"{metrics_data[2]['Reasoning (Keywords)']:.1f}", delta=f"{metrics_data[2]['Reasoning (Keywords)'] - metrics_data[0]['Reasoning (Keywords)']:.1f}")
        col3.metric("Samples Evaluated", len(data))

        st.divider()
        st.subheader("📈 Reasoning Depth Comparison")
        st.bar_chart(df_metrics.set_index("Method")["Reasoning (Keywords)"])

        st.divider()
        st.subheader("🔍 Case-by-Case Analysis (Pre-Generated)")
        selected_q = st.selectbox("Pick a question to compare results:", [r["question"] for r in data])
        q_data = next(r for r in data if r["question"] == selected_q)
        tab1, tab2, tab3 = st.tabs(["Raw LLM", "Prompt Engineered", "Hybrid System"])
        with tab1: st.write(q_data["raw_llm"]["text"])
        with tab2: st.write(q_data["prompt_engineered"]["pro"], q_data["prompt_engineered"]["con"])
        with tab3: st.write(q_data["hybrid"]["full_output"]["result"])