While this multi-agent AI framework demonstrates robust capabilities, it is subject to several fundamental limitations that are important to consider for rigorous academic evaluation.

### 🧠 1. Dependence on Prompt Quality
The overall performance of the system relies heavily on the quality of the prompts provided to the agents. Suboptimal prompt design can directly compromise the structural integrity and reasoning of the output.

### 📊 2. Synthetic Dataset Bias
The machine learning predictions may exhibit inherent biases, as the underlying training dataset is synthetically generated rather than derived from organically labeled real-world data.

### 📚 3. Limited Factual Grounding
The system operates without an external factual grounding mechanism, such as Retrieval-Augmented Generation (RAG). Consequently, the agents may occasionally generate generic or factually unsupported claims.

### 📏 4. Evaluation Metric Limitations
Our quantitative evaluation relies on traditional NLP metrics, such as BLEU and ROUGE, which primarily measure lexical overlap rather than the true correctness or logical depth of the reasoning.

### 💻 5. Computational Constraints
Due to computational constraints, the framework relies on lightweight, localized language models rather than state-of-the-art, large-scale foundational models, which may inherently limit the depth of its analytical reasoning.
