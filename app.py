import streamlit as st
from orchestrator.pipeline import run_debate

st.set_page_config(page_title="Multi-Agent Debate System", page_icon="🧠", layout="wide")
st.title("🧠 Multi-Agent Debate System")

question = st.text_input("Enter your question:", placeholder="e.g., Is React the best framework?")

if st.button("Run Debate"):
    if not question:
        st.warning("Please enter a question first.")
    else:
        with st.status("🤖 AI Agents are debating (Structured Mode)...", expanded=True) as status:
            st.write("Generating structured JSON arguments...")
            try:
                output = run_debate(question)
                status.update(label="✅ Debate Complete!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="❌ Error occurred", state="error", expanded=True)
                st.error(f"Failed to run debate: {e}")
                st.stop()

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
        st.subheader("⚖️ Final Decision")
        
        res = output["result"]
        with st.container(border=True):
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Winner", res["winner"])
            col_b.metric("Pro Score", res["scores"]["pro"])
            col_c.metric("Con Score", res["scores"]["con"])
            
            st.write(f"**Reason:** {res['reason']}")
            st.caption(f"Decision Method: {res['decision_type'].replace('_', ' ').title()} | Confidence: {res['confidence']*100}%")