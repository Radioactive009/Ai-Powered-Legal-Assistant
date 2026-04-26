import json
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def load_data(filepath):
    """
    Loads features and labels from JSON.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    X = []
    y = []
    
    for entry in data:
        # Extract features (all keys except 'label')
        features = [
            entry["pro_length"], entry["con_length"],
            entry["pro_avg_len"], entry["con_avg_len"],
            entry["pro_reason_len"], entry["con_reason_len"],
            entry["pro_impact_len"], entry["con_impact_len"],
            entry["pro_keywords"], entry["con_keywords"]
        ]
        X.append(features)
        y.append(entry["label"])
        
    return X, y

def train_and_save_model(X, y, model_path):
    """
    Trains a Logistic Regression model and saves it.
    """
    # Train-Test Split (80-20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")

    # Initialize and train model with class weight balancing
    model = LogisticRegression(class_weight='balanced', max_iter=1000)
    model.fit(X_train, y_train)

    # Evaluation
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions)
    cm = confusion_matrix(y_test, predictions)

    print(f"\nModel Accuracy: {acc:.2f}")
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    print(report)

    # Save model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Model saved to: {model_path}")

def main():
    # Automatically resolve paths relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_file = os.path.join(current_dir, "..", "dataset", "features.json")
    model_output = os.path.join(current_dir, "model.pkl")

    try:
        X, y = load_data(input_file)
        train_and_save_model(X, y, model_output)
    except Exception as e:
        print(f"Error during training: {e}")

if __name__ == "__main__":
    main()
