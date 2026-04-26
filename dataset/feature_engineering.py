import json
import os

def extract_features_from_side(arguments):
    """
    Extracts numerical features from a list of structured arguments.
    """
    if not arguments:
        return {
            "length": 0,
            "avg_len": 0,
            "reason_len": 0,
            "impact_len": 0,
            "keywords": 0
        }

    keywords_to_track = ["because", "therefore", "leads to", "results in"]
    
    total_words = 0
    total_reason_words = 0
    total_impact_words = 0
    total_keywords = 0
    num_args = len(arguments)

    for arg in arguments:
        p = arg.get("point", "")
        r = arg.get("reason", "")
        i = arg.get("impact", "")

        # Full text for word count and keyword search
        full_text = f"{p} {r} {i}".lower()
        
        # Word counts
        p_words = len(p.split())
        r_words = len(r.split())
        i_words = len(i.split())
        
        total_words += (p_words + r_words + i_words)
        total_reason_words += r_words
        total_impact_words += i_words

        # Keyword counting
        for kw in keywords_to_track:
            total_keywords += full_text.count(kw)

    return {
        "length": total_words,
        "avg_len": total_words / num_args if num_args > 0 else 0,
        "reason_len": total_reason_words / num_args if num_args > 0 else 0,
        "impact_len": total_impact_words / num_args if num_args > 0 else 0,
        "keywords": total_keywords
    }

def perform_feature_engineering():
    # Automatically find the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_path = os.path.join(current_dir, "debate_dataset_cleaned.json")
    output_path = os.path.join(current_dir, "features.json")

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        raw_dataset = json.load(f)

    processed_features = []

    for debate in raw_dataset:
        pro_feats = extract_features_from_side(debate.get("pro", []))
        con_feats = extract_features_from_side(debate.get("con", []))
        
        # Combine into a single feature vector
        feature_vector = {
            "pro_length": pro_feats["length"],
            "con_length": con_feats["length"],
            "pro_avg_len": pro_feats["avg_len"],
            "con_avg_len": con_feats["avg_len"],
            "pro_reason_len": pro_feats["reason_len"],
            "con_reason_len": con_feats["reason_len"],
            "pro_impact_len": pro_feats["impact_len"],
            "con_impact_len": con_feats["impact_len"],
            "pro_keywords": pro_feats["keywords"],
            "con_keywords": con_feats["keywords"],
            "label": 1 if debate.get("winner") == "Pro" else 0
        }
        
        processed_features.append(feature_vector)

    # Save to JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed_features, f, indent=4)

    print(f"Feature engineering complete.")
    print(f"Processed {len(processed_features)} samples.")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    perform_feature_engineering()
