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

# --- UTILS FOR LIVE COMPARISON & METRICS ---
def count_keywords(text):
    keywords = ["because", "leads to", "results in", "therefore"]
    text = str(text).lower()
    return sum(text.count(k) for k in keywords)

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
        text = response.json().get("response", "")
        return text, {"length": len(text.split()), "keywords": count_keywords(text)}
    except:
        return "Error fetching Raw LLM response.", {"length": 0, "keywords": 0}

def get_prompt_only(question):
    pro = generate_pro_argument(question)
    con = generate_con_argument(question)
    full_text = str(pro) + " " + str(con)
    return pro, con, {"length": len(full_text.split()), "keywords": count_keywords(full_text)}

# --- SIDEBAR ---
st.sidebar.title("🛠️ Project Menu")
page = st.sidebar.radio("Go to:", ["Debate Arena", "Evaluation Dashboard"])

# --- PAGE 1: DEBATE ARENA ---
if page == "Debate Arena":
    st.title("🧠 Multi-Agent Debate System")
    st.caption("Hybrid Intelligent Mode: Rules + Machine Learning + LLM Tie-Breaker")

    question = st.text_input("Enter your question:", placeholder="e.g., Is React the best framework?")
    
    compare_mode = st.checkbox("🔍 Run Real-Time Comparison Mode (Show Live Graphs & Metrics)")

    if st.button("Run Debate"):
        if not question:
            st.warning("Please enter a question first.")
        else:
            if compare_mode:
                with st.status("🔬 Performing Comparative Analysis & Generating Visuals...", expanded=True) as status:
                    st.write("1/3: Analyzing Raw LLM baseline...")
                    raw_text, raw_m = get_raw_llm(question)
                    
                    st.write("2/3: Analyzing Prompt-Engineered baseline...")
                    p_pro, p_con, p_m = get_prompt_only(question)
                    
                    st.write("3/3: Executing Hybrid Intelligent Pipeline...")
                    hybrid_out = run_debate(question)
                    h_text = str(hybrid_out["pro"]) + " " + str(hybrid_out["con"])
                    h_m = {"length": len(h_text.split()), "keywords": count_keywords(h_text)}
                    
                    status.update(label="✅ Comparison & Analytics Complete!", state="complete", expanded=False)

                # --- NEW: LIVE GRAPHS SECTION ---
                st.subheader("📊 Live Performance Comparison")
                
                # Prepare data for graph
                chart_data = pd.DataFrame({
                    "Method": ["Raw LLM", "Prompt Engineered", "Hybrid System"],
                    "Reasoning Depth (Keywords)": [raw_m["keywords"], p_m["keywords"], h_m["keywords"]],
                    "Structural Length (Words)": [raw_m["length"], p_m["length"], h_m["length"]]
                })

                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write("**Reasoning Depth (Logical Connectors Used)**")
                    st.bar_chart(chart_data.set_index("Method")["Reasoning Depth (Keywords)"])
                with c2:
                    st.write("**Quick Insights**")
                    st.metric("Hybrid Advantage", f"+{h_m['keywords'] - raw_m['keywords']} Keywords")
                    st.metric("Structure Gain", f"+{h_m['length'] - raw_m['length']} Words")
                
                st.divider()

                # Show Results in Tabs
                tab_h, tab_p, tab_r = st.tabs(["⭐ Hybrid System (Winner Selected)", "📝 Prompt Only", "📄 Raw LLM"])
                
                with tab_r:
                    st.info("Raw LLM Output (No constraints)")
                    st.write(raw_text)

                with tab_p:
                    st.info("Prompt Engineered (Structure only)")
                    col_p1, col_p2 = st.columns(2)
                    col_p1.write(p_pro)
                    col_p2.write(p_con)

                with tab_h:
                    st.success("Hybrid Intelligent System (Winner Selected)")
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
                # Normal Mode
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
    results_path = os.path.join("evaluation", "results.json")
    if os.path.exists(results_path):
        with open(results_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        methods = ["raw_llm", "prompt_engineered", "hybrid"]
        metrics_data = []
        for m in methods:
            avg_kw = sum(r[m]["metrics"]["keywords"] for r in data) / len(data)
            metrics_data.append({"Method": m.title(), "Reasoning (Keywords)": avg_kw})
        df_metrics = pd.DataFrame(metrics_data)
        st.subheader("📈 Reasoning Depth Comparison (Historical Data)")
        st.bar_chart(df_metrics.set_index("Method")["Reasoning (Keywords)"])