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

# 1. LOAD DATASET
def load_and_prepare_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return None
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    formatted_data = []
    for item in data:
        # Use Pro arguments for instruction tuning
        pro_text = json.dumps(item.get("pro", []), indent=2)
        instruction = f"Generate arguments for: {item.get('question')}\n\nArguments:\n{pro_text}"
        formatted_data.append({"text": instruction})
        
    return Dataset.from_list(formatted_data)

# 2. MAIN TRAINING FUNCTION
def train():
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    dataset_path = os.path.join("..", "dataset", "debate_dataset_cleaned.json")
    
    print(f"Loading model: {model_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Load model (use CPU if no GPU available)
    device_map = "auto" if torch.cuda.is_available() else "cpu"
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map=device_map)

    # 3. APPLY LoRA CONFIG
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 4. PREPARE DATASET
    dataset = load_and_prepare_data(dataset_path)
    if dataset is None: return
    
    def tokenize_func(examples):
        return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=256)
    
    tokenized_dataset = dataset.map(tokenize_func, batched=True)

    # 5. TRAINING ARGUMENTS
    training_args = TrainingArguments(
        output_dir="./lora_model",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        num_train_epochs=1, # Keep it low for demo
        logging_steps=10,
        save_strategy="epoch",
        fp16=torch.cuda.is_available(), # Use half precision if GPU
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )

    print("Starting Fine-tuning (LoRA)...")
    if not torch.cuda.is_available():
        print("WARNING: No GPU detected. Training on CPU will be EXTREMELY slow.")
    
    trainer.train()
    
    # SAVE THE LoRA ADAPTER
    model.save_pretrained("./lora_model")
    print("LoRA Fine-tuning complete. Model saved to ./lora_model")

if __name__ == "__main__":
    train()
