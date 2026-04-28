import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize the model globally so it's loaded once
MODEL_NAME = 'all-MiniLM-L6-v2'
try:
    model = SentenceTransformer(MODEL_NAME)
except Exception as e:
    print(f"Warning: Could not load SentenceTransformer model: {e}")
    model = None

VECTOR_DB_DIR = os.path.dirname(__file__)
INDEX_PATH = os.path.join(VECTOR_DB_DIR, "debate_index.faiss")
METADATA_PATH = os.path.join(VECTOR_DB_DIR, "metadata.json")

def build_index():
    """
    Builds the FAISS index from the cleaned debate dataset.
    """
    dataset_path = os.path.join(VECTOR_DB_DIR, "..", "dataset", "debate_dataset_cleaned.json")
    if not os.path.exists(dataset_path):
        print("Dataset not found. Cannot build FAISS index.")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # We use dimension 384 for MiniLM-L6-v2
    dimension = 384
    # faiss uses IndexFlatL2 for fast L2 similarity search
    index = faiss.IndexFlatL2(dimension)
    
    metadata = {}
    embeddings = []

    print(f"Building FAISS index for {len(data)} debates...")
    
    for i, item in enumerate(data):
        question = item.get("question", "")
        pro_args = item.get("pro", [])
        con_args = item.get("con", [])
        
        # Combine text: Question + Pro arguments + Con arguments
        pro_text = " ".join([f"{arg.get('point', '')} {arg.get('reason', '')} {arg.get('impact', '')}" for arg in pro_args])
        con_text = " ".join([f"{arg.get('point', '')} {arg.get('reason', '')} {arg.get('impact', '')}" for arg in con_args])
        
        combined_text = f"Question: {question} Pro: {pro_text} Con: {con_text}"
        
        # Generate embedding
        embedding = model.encode(combined_text)
        embeddings.append(embedding)
        
        # Maintain mapping: id -> original text/data
        metadata[str(i)] = {
            "question": question,
            "pro_text": pro_text,
            "con_text": con_text
        }

    if embeddings:
        # Add embeddings to index
        embeddings_matrix = np.array(embeddings).astype('float32')
        index.add(embeddings_matrix)
        
        # Save index and metadata
        faiss.write_index(index, INDEX_PATH)
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
        print(f"Index successfully built and saved to {INDEX_PATH}")
        print(f"Metadata saved to {METADATA_PATH}")

def search_similar(query, top_k=3):
    """
    Searches the FAISS index for the most similar past debates.
    """
    if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
        print("FAISS index or metadata not found. Please run build_index() first.")
        return []

    if model is None:
        return []

    # Load index and metadata
    index = faiss.read_index(INDEX_PATH)
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Encode query
    query_embedding = model.encode([query]).astype('float32')
    
    # Search FAISS index
    distances, indices = index.search(query_embedding, top_k)
    
    # Return top_k similar debates
    results = []
    for i, idx in enumerate(indices[0]):
        str_idx = str(idx)
        if str_idx in metadata:
            results.append({
                "id": str_idx,
                "distance": float(distances[0][i]),
                "data": metadata[str_idx]
            })
            
    return results

if __name__ == "__main__":
    # Ensure the directory exists
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)
    build_index()

'''
--- EXPLANATION ---
* Why FAISS is used: FAISS (Facebook AI Similarity Search) is a highly optimized library for extremely fast similarity search and clustering of dense vectors. When we use LLMs or sentence transformers to create embeddings (lists of numbers), FAISS allows the system to instantly scan thousands of vectors to find the closest matches in milliseconds.
* How it improves the system (Context Awareness): By embedding past arguments, the debate system gains "vector-based memory". Before answering a new question, it can retrieve historically successful arguments or similar past debates to avoid repeating weak points, ultimately enhancing retrieval intelligence and context awareness.
'''
