import json
import time
import sys
import os
import random

# Add parent directory to path so we can import orchestrator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator.pipeline import run_debate

def generate_dataset():
    # expanded list of diverse questions (approx 125 questions)
    questions = [
        # Technology
        "Is AI dangerous to humanity?", "Should Python replace all other languages?", "Is space exploration worth the cost?",
        "Should cryptocurrencies be regulated?", "Is 5G harmful to health?", "Will automation lead to mass unemployment?",
        "Is open-source better than proprietary?", "Should facial recognition be banned?", "Is nuclear energy the future?",
        "Should social media algorithms be public?", "Is the Metaverse inevitable?", "Should AI have copyright over its art?",
        "Is cloud computing safer than local storage?", "Should electric vehicles be mandatory by 2035?", "Is quantum computing a security threat?",
        "Should robots have legal rights?", "Is Starlink better than traditional fiber?", "Should smartphones be banned for children under 12?",
        "Is the internet a basic human right?", "Should biotech companies be allowed to patent genes?", "Is virtual reality better than real-life travel?",
        "Should drones be used for local deliveries?", "Is cybersecurity the biggest threat to world peace?", "Should tech giants be taxed more?", "Is web3 a scam?",
        
        # Education
        "Should college be free for everyone?", "Are online degrees as valuable as traditional ones?", "Should coding be mandatory in school?",
        "Is homework beneficial?", "Should standard testing be abolished?", "Are private schools better?", "Should teachers be replaced by AI?",
        "Is physical education important?", "Should students use phones in class?", "Is a gap year beneficial?",
        "Should financial literacy be taught in high school?", "Is homeschooling better than public school?", "Should university entrance exams be removed?",
        "Is learning a second language necessary in the age of AI translation?", "Should schools move to a 4-day week?", "Is tenure for professors a good idea?",
        "Should vocational training be prioritized over liberal arts?", "Is self-teaching more effective than structured schooling?", "Should arts education be mandatory?",
        "Is the cost of higher education worth the investment?", "Should all textbooks be digital?", "Is grading students a fair way to measure intelligence?",
        "Should schools focus more on soft skills than academic subjects?", "Is the 'flipped classroom' model effective?", "Should sex education be mandatory in all schools?",
        
        # Ethics
        "Is animal testing ethical?", "Should the death penalty be abolished?", "Is genetic engineering acceptable?",
        "Should euthanasia be legalized?", "Is privacy more important than security?", "Should rich countries provide aid?",
        "Is it ethical to consume meat?", "Should censorship exist?", "Is fast fashion ethical?", "Should wealth be redistributed?",
        "Is it ethical to use AI to write books?", "Should humanity attempt to colonize Mars?", "Is it moral to lie to protect someone?",
        "Should companies be allowed to track user behavior for ads?", "Is the consumption of luxury goods unethical?", "Should plastic be banned entirely?",
        "Is it ethical to choose the gender of your baby?", "Should zoos be closed?", "Is it right to limit the number of children people can have?",
        "Should whistleblowers be protected by law?", "Is it ethical to build killer robots for defense?", "Should surrogacy be legal?",
        "Is cultural appropriation always wrong?", "Should historical monuments of controversial figures be removed?", "Is it ethical to experiment on human embryos?",
        
        # Business
        "Is remote work better than office work?", "Should minimum wage be increased?", "Is a 4-day work week productive?",
        "Should CEOs have a salary cap?", "Is capitalism the best system?", "Should big tech be broken up?",
        "Is influencer marketing effective?", "Should corporations be responsible for climate change?", "Is job hopping good?",
        "Should unpaid internships be illegal?", "Is the gig economy exploitative?", "Should brands take political stances?",
        "Is remote work making us less productive?", "Should advertising to children be banned?", "Is the customer always right?",
        "Should work-from-home employees be paid less?", "Is a universal basic income a good idea?", "Should the retirement age be lowered?",
        "Is entrepreneurship for everyone?", "Should business ethics be a mandatory course?", "Is competition always good for the consumer?",
        "Should companies be forced to disclose their gender pay gap?", "Is the stock market a reliable indicator of economic health?", "Should small businesses get more tax breaks?", "Is office gossip harmful to productivity?",
        
        # Lifestyle
        "Is a vegan diet better?", "Should everyone live in cities?", "Is social media making us lonely?",
        "Should we strive for minimalism?", "Is gaming a productive hobby?", "Should mental health days be mandatory?",
        "Is travel a necessity?", "Should cities be car-free?", "Is reading books better than movies?", "Should we prioritize work-life balance?",
        "Is coffee addiction a serious problem?", "Should public transport be free?", "Is living in a tiny house a good idea?",
        "Should children be allowed to be influencers?", "Is the trend of 'hustle culture' toxic?", "Should people stop using plastic bottles?",
        "Is meditation essential for mental health?", "Should weekends be three days long?", "Is traditional marriage still relevant?",
        "Should junk food be taxed like cigarettes?", "Is living in the suburbs better than the city?", "Should everyone be required to do military service?",
        "Is organic food worth the extra price?", "Should social media accounts require real ID?", "Is the 'digital nomad' lifestyle sustainable?"
    ]

    raw_dataset = []
    total_q = len(questions)

    print(f"Starting dataset generation for {total_q} questions...\n")

    for i, q in enumerate(questions):
        print(f"Processing ({i+1}/{total_q}): {q}")
        try:
            debate_result = run_debate(q)
            entry = {
                "question": debate_result["question"],
                "pro": debate_result["pro"],
                "con": debate_result["con"],
                "winner": debate_result["result"]["winner"]
            }
            raw_dataset.append(entry)
            print(f"   -> Result: {entry['winner']} wins.")
        except Exception as e:
            print(f"   -> Error: {e}")
        time.sleep(1)

    # Balancing logic
    pro_samples = [d for d in raw_dataset if d["winner"] == "Pro"]
    con_samples = [d for d in raw_dataset if d["winner"] == "Con"]

    print("\n--- Generation Statistics ---")
    print(f"Total processed: {len(raw_dataset)}")
    print(f"Pro winners: {len(pro_samples)}")
    print(f"Con winners: {len(con_samples)}")

    # Balance the dataset (50/50)
    min_size = min(len(pro_samples), len(con_samples))
    balanced_dataset = pro_samples[:min_size] + con_samples[:min_size]
    random.shuffle(balanced_dataset)

    print(f"\nBalanced Dataset Result:")
    print(f"Total: {len(balanced_dataset)}")
    print(f"Pro: {min_size}")
    print(f"Con: {min_size}")

    # Save cleaned dataset
    cleaned_path = os.path.join(os.path.dirname(__file__), 'debate_dataset_cleaned.json')
    with open(cleaned_path, 'w', encoding='utf-8') as f:
        json.dump(balanced_dataset, f, indent=4)

    print(f"\nSaved cleaned dataset to: {cleaned_path}")

if __name__ == "__main__":
    generate_dataset()
