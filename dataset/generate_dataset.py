import json
import time
import sys
import os

# Add parent directory to path so we can import orchestrator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator.pipeline import run_debate

def generate_dataset():
    # List of diverse questions across categories
    questions = [
        # Technology
        "Is AI dangerous to humanity?",
        "Should Python replace all other programming languages?",
        "Is space exploration worth the cost?",
        "Should cryptocurrencies be regulated?",
        "Is 5G technology harmful to health?",
        "Will automation lead to mass unemployment?",
        "Is open-source software better than proprietary software?",
        "Should facial recognition technology be banned?",
        "Is nuclear energy the future of green power?",
        "Should social media algorithms be public?",
        
        # Education
        "Should college be free for everyone?",
        "Are online degrees as valuable as traditional ones?",
        "Should coding be a mandatory subject in school?",
        "Is homework beneficial for student learning?",
        "Should standard testing be abolished?",
        "Are private schools better than public schools?",
        "Should teachers be replaced by AI in the future?",
        "Is physical education important in schools?",
        "Should students be allowed to use phones in class?",
        "Is a gap year beneficial for students?",
        
        # Ethics
        "Is animal testing ethical for medical research?",
        "Should the death penalty be abolished?",
        "Is genetic engineering in humans acceptable?",
        "Should euthanasia be legalized globally?",
        "Is privacy more important than security?",
        "Should rich countries provide aid to poor countries?",
        "Is it ethical to consume meat?",
        "Should censorship exist on the internet?",
        "Is fast fashion ethical?",
        "Should wealth be redistributed through high taxes?",
        
        # Business
        "Is remote work better than office work?",
        "Should the minimum wage be increased?",
        "Is a 4-day work week productive?",
        "Should CEOs have a salary cap?",
        "Is capitalism the best economic system?",
        "Should big tech companies be broken up?",
        "Is influencer marketing effective?",
        "Should corporations be held responsible for climate change?",
        "Is job hopping good for your career?",
        "Should unpaid internships be illegal?",
        
        # Lifestyle
        "Is a vegan diet better for the environment?",
        "Should everyone live in cities?",
        "Is social media making us more lonely?",
        "Should we strive for a minimalist lifestyle?",
        "Is gaming a productive hobby?",
        "Should mental health days be mandatory at work?",
        "Is travel a necessity for personal growth?",
        "Should cities be car-free?",
        "Is reading books better than watching movies?",
        "Should we prioritize work-life balance over career growth?"
    ]

    dataset = []
    total = len(questions)

    print(f"Starting dataset generation for {total} questions...\n")

    for i, q in enumerate(questions):
        print(f"Processing ({i+1}/{total}): {q}")
        
        try:
            # Run the debate pipeline
            debate_result = run_debate(q)
            
            # Extract the required structured data
            entry = {
                "question": debate_result["question"],
                "pro": debate_result["pro"],
                "con": debate_result["con"],
                "winner": debate_result["result"]["winner"]
            }
            
            dataset.append(entry)
            print(f"   -> Result: {entry['winner']} wins. Saved {len(dataset)} samples.")
            
        except Exception as e:
            print(f"   -> Error processing '{q}': {e}")

        # Small delay to avoid overloading local Ollama
        time.sleep(1)

    # Save the dataset to JSON
    output_path = os.path.join(os.path.dirname(__file__), 'debate_dataset.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=4)

    print(f"\nSuccessfully generated dataset with {len(dataset)} samples.")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    generate_dataset()
