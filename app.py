import streamlit as st
from orchestrator.pipeline import run_debate

st.set_page_config(page_title="Multi-Agent Debate System", page_icon="🧠")
st.title("🧠 Multi-Agent Debate System")

question = st.text_input("Enter your question:", placeholder="e.g., Should AI replace teachers?")

if st.button("Run Debate"):
    if not question:
        st.warning("Please enter a question first.")
    else:
        with st.status("🤖 AI Agents are debating...", expanded=True) as status:
            st.write("Generating Pro and Con arguments in parallel...")
            output = run_debate(question)
            status.update(label="✅ Debate Complete!", state="complete", expanded=False)

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📌 Pro Arguments")
            st.info(output["pro"])

        with col2:
            st.subheader("📌 Con Arguments")
            st.warning(output["con"])

        st.divider()
        st.subheader("⚖️ Final Decision")
        st.success(output["result"])