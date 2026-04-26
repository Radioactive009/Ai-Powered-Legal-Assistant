import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def run_inference(question):
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    adapter_path = "./lora_model" # Path to your saved LoRA weights

    print(f"Loading Base Model: {model_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    base_model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")

    try:
        print("Loading LoRA Adapters...")
        model = PeftModel.from_pretrained(base_model, adapter_path)
    except Exception as e:
        print(f"Warning: Could not load adapters (Did you finish training?): {e}")
        model = base_model # Fallback to base model

    input_text = f"Generate arguments for: {question}\n\nArguments:\n"
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

    print("Generating...")
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=200, 
            temperature=0.7, 
            do_sample=True
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    print("\n--- Model Output ---")
    print(response)

if __name__ == "__main__":
    q = "Is AI better than humans?"
    run_inference(q)
