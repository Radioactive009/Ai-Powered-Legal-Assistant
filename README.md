# ⚖️ AI-Powered Legal Assistant: Multi-Agent Debate System

An advanced, hybrid AI framework that utilizes autonomous agents to dialectically debate complex legal and policy questions. The system leverages a multi-tiered evaluation pipeline combining deterministic rules, machine learning, and Large Language Models (LLMs) to intelligently analyze and select the most logically sound arguments.

## 🚀 Key Features

* **🤖 Autonomous Debate Generation**: Pro and Con agents automatically generate structured, multi-dimensional arguments for any given prompt.
* **⚖️ Hybrid Judge System**: A robust 3-tier evaluation mechanism:
  * **Rule-Based Scoring**: Evaluates structural complexity, length, and keyword reasoning.
  * **Machine Learning Prediction**: Pattern recognition utilizing extracted features to predict the strongest argument.
  * **LLM Tiebreaker**: Resolves mathematical ties via deep semantic analysis.
* **🧠 Dynamic FAISS Vector Memory**: The system learns over time. Debates are autonomously embedded (using `sentence-transformers`) and stored in a live FAISS index, allowing the system to retrieve past context and avoid duplicates.
* **📊 Interactive Streamlit Dashboard**: A clean frontend featuring a live Debate Arena, real-time comparison metrics (Raw vs. Prompt vs. Hybrid), and academic evaluation dashboards.
* **🚀 LoRA Fine-Tuning**: Integrates custom-trained, lightweight models that consistently outperform base models in structural formatting and reasoning depth.

## 📂 Project Structure

```text
├── agents/             # Pro and Con argument generation logic
├── dataset/            # Training datasets and feature engineering tools
├── evaluation/         # Academic metrics, BLEU/ROUGE scoring, and baselines
├── finetune/           # LoRA fine-tuning scripts for the LLM
├── judge/              # Hybrid evaluation logic (Rule-based & LLM tiebreaker)
├── ml/                 # Machine learning models for pattern prediction
├── orchestrator/       # Core pipeline integrating agents, memory, and judges
├── vector_db/          # FAISS vector database and dynamic memory storage
├── app.py              # Streamlit frontend dashboard
└── README.md           # Project documentation
```

## ⚙️ How It Works (Pipeline)

1. **Input**: A stakeholder or user submits a complex question.
2. **Context Retrieval**: The system queries the FAISS database to surface similar historical debates.
3. **Agent Generation**: Pro and Con agents generate arguments, explicitly outlining the *Point*, *Reason*, and *Impact*.
4. **Evaluation**: The Hybrid Judge mathematically and semantically evaluates the arguments.
5. **Memory Storage**: Non-duplicate debates are permanently stored into the live FAISS memory.
6. **Decision**: The optimal policy decision and metrics are presented on the frontend.

## 🌍 Real-World Application

This system provides substantial value in **Policy Decision Support**. By automating the dialectical process, it actively reduces human cognitive bias, improves decision transparency, and provides policymakers with a clear, balanced, and evidence-driven overview of complex issues.

## ⚠️ System Limitations

For rigorous academic evaluation, note the following constraints:
* **Prompt Dependence:** Output quality relies heavily on initial prompt engineering.
* **Synthetic Bias:** The training dataset is synthetically generated, which may introduce predictive biases.
* **No External RAG:** The system lacks real-time factual grounding via external web search.
* **Lightweight Models:** Relies on local, lightweight models rather than large-scale commercial foundational models.

## 💻 Getting Started

To run the interactive dashboard locally:

```bash
# Start the Streamlit frontend
streamlit run app.py
```
