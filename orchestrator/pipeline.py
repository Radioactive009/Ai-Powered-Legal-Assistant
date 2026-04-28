import pickle
import os
import numpy as np
import json
import pandas as pd
import shap
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from agents.pro_agent import generate_pro_argument
from agents.con_agent import generate_con_argument
from judge.rule_judge import rule_based_judge
from judge.llm_judge import llm_tiebreaker
from dataset.feature_engineering import extract_features_from_side
from vector_db.faiss_store import search_similar, add_to_memory

ENABLE_LIVE_MEMORY = True

# Load the ML model once at module level
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "model.pkl")
try:
    with open(MODEL_PATH, "rb") as f:
        ml_model = pickle.load(f)
        
    FEATURE_NAMES = ['Pro Length', 'Con Length', 'Pro Avg Len', 'Con Avg Len', 
                     'Pro Reason Len', 'Con Reason Len', 'Pro Impact Len', 'Con Impact Len', 
                     'Pro Keywords', 'Con Keywords']
                     
    features_path = os.path.join(os.path.dirname(__file__), "..", "dataset", "features.json")
    with open(features_path, "r", encoding="utf-8") as f:
        features_data = json.load(f)
        
    df_bg = pd.DataFrame(features_data)
    X_background = df_bg.drop(columns=["label"]).values
    
    explainer = shap.Explainer(ml_model, X_background, feature_names=FEATURE_NAMES)
except Exception as e:
    print(f"Warning: Could not load ML model or SHAP explainer: {e}")
    ml_model = None
    explainer = None

def extract_features(pro_args, con_args):
    """
    Converts debate arguments into the exact feature vector used during ML training.
    """
    pro_feats = extract_features_from_side(pro_args)
    con_feats = extract_features_from_side(con_args)
    
    return [
        pro_feats["length"], con_feats["length"],
        pro_feats["avg_len"], con_feats["avg_len"],
        pro_feats["reason_len"], con_feats["reason_len"],
        pro_feats["impact_len"], con_feats["impact_len"],
        pro_feats["keywords"], con_feats["keywords"]
    ]

def run_debate(question, enable_live_memory=None):
    """
    Hybrid intelligent pipeline combining Rule-based, ML-based, and LLM-based judging.
    """
    # FAISS Vector DB Integration: Retrieve past similar debates for context
    try:
        similar_debates = search_similar(question, top_k=2)
        if similar_debates:
            print(f"Retrieved {len(similar_debates)} similar past debates from FAISS.")
            # This context can now be utilized by the agents or the judge for a more informed decision
    except Exception as e:
        similar_debates = []
        print(f"FAISS search failed: {e}")

    with ThreadPoolExecutor() as executor:
        future_pro = executor.submit(generate_pro_argument, question)
        future_con = executor.submit(generate_con_argument, question)
        
        pro_output = future_pro.result()
        con_output = future_con.result()

    # 1. Rule-Based Scoring
    rule_res = rule_based_judge(pro_output, con_output)
    pro_score = rule_res["scores"]["pro"]
    con_score = rule_res["scores"]["con"]
    rule_winner = rule_res["winner"]

    # 2. ML Prediction
    ml_prediction_label = "Unknown"
    shap_values_out = None
    if ml_model:
        features = extract_features(pro_output, con_output)
        pred = ml_model.predict([features])[0]
        ml_prediction_label = "Pro" if pred == 1 else "Con"
        
        if explainer:
            try:
                shap_values = explainer(np.array([features]))
                shap_values_out = shap_values[0]
            except Exception as e:
                print(f"SHAP error: {e}")

    # 3. Decision Logic (Hybrid Integration)
    if rule_winner == ml_prediction_label:
        final_winner = rule_winner
        decision_type = "rule+ml_agreement"
        reason = f"Both rule-based scoring and ML model agreed on {final_winner} as the winner."
    else:
        # Conflict between Rules and ML
        if abs(pro_score - con_score) < 0.05:
            # Scores are too close, use LLM as final arbiter
            final_winner = llm_tiebreaker(question, pro_output, con_output)
            decision_type = "llm_tiebreaker"
            reason = "Rules and ML disagreed, and scores were near-equal. LLM tie-breaker was used for semantic judgment."
        else:
            # Rules and ML disagree, but scores have a clear lead - ML overrides
            final_winner = ml_prediction_label
            decision_type = "ml_override"
            reason = f"ML model overrode rule-based scoring to select {final_winner} based on learned patterns."

    if enable_live_memory is None:
        enable_live_memory = ENABLE_LIVE_MEMORY

    if enable_live_memory:
        added = add_to_memory(question, pro_output, con_output)
        if added:
            print("Saved to memory")

    return {
        "question": question,
        "similar_debates": similar_debates,
        "pro": pro_output,
        "con": con_output,
        "result": {
            "winner": final_winner,
            "scores": {
                "pro": pro_score,
                "con": con_score
            },
            "ml_prediction": ml_prediction_label,
            "decision_type": decision_type,
            "confidence": max(pro_score, con_score),
            "reason": reason,
            "shap_values": shap_values_out
        }
    }