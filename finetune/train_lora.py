import os
import torch
import json
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType

# 1. LOAD DATASET (Limited for Fast CPU Training)
def load_and_prepare_data(file_path):
    if not os.path.exists(file_path):
        return None
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Take only the first 5 samples for an ultra-fast demo on CPU
    fast_data = data[:5]
    
    formatted_data = []
    for item in fast_data:
        pro_text = json.dumps(item.get("pro", [])[:1], indent=1) # Minimal text
        instruction = f"Question: {item.get('question')}\nArgs: {pro_text}"
        formatted_data.append({"text": instruction})
        
    return Dataset.from_list(formatted_data)

# 2. MAIN TRAINING FUNCTION (Optimized for CPU)
def train():
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    dataset_path = os.path.join("..", "dataset", "debate_dataset_cleaned.json")
    
    print(f"Loading model: {model_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Load model on CPU
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map={"": "cpu"})

    # 3. APPLY LoRA
    lora_config = LoraConfig(
        r=4, # Reduced rank for speed
        lora_alpha=8,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        task_type=TaskType.CAUSAL_LM
    )
    
    model = get_peft_model(model, lora_config)
    
    # 4. PREPARE DATASET
    dataset = load_and_prepare_data(dataset_path)
    if dataset is None: return
    
    def tokenize_func(examples):
        return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=64) # Short tokens
    
    tokenized_dataset = dataset.map(tokenize_func, batched=True)

    # 5. TRAINING ARGUMENTS (Ultra-Fast CPU Mode)
    training_args = TrainingArguments(
        output_dir="./lora_model",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        learning_rate=1e-4,
        num_train_epochs=1,
        logging_steps=1,
        save_strategy="no", # Save manually at the end
        use_cpu=True,
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )

    print("\n--- STARTING ULTRA-FAST CPU TRAINING ---")
    print("This will take approx 2-3 minutes...")
    
    trainer.train()
    
    # SAVE
    model.save_pretrained("./lora_model")
    print("\n✅ Fine-tuning complete! Model saved to ./lora_model")

if __name__ == "__main__":
    train()
