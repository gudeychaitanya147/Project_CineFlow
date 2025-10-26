from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# ------------------------------
# Load the model (MPT-7B-Chat)
# ------------------------------
model_name = "mosaicml/mpt-7b-chat"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("Loading model on GPU...")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",        # automatically uses GPU
    dtype=torch.float16 # half precision for 8GB GPU
)
model.eval()
print("Model loaded successfully!")

# ------------------------------
# Chat function
# ------------------------------
def chat(prompt, max_tokens=200):
    """
    Simple function to chat with the local MPT-7B-Chat model.
    
    Args:
        prompt (str): Your prompt/question.
        max_tokens (int): Maximum tokens to generate.
        
    Returns:
        str: Model response.
    """
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# ------------------------------
# Optional interactive mode
# ------------------------------
if __name__ == "__main__":
    print("Welcome to local MPT-7B-Chat! Type 'exit' to quit.")
    while True:
        prompt = input("You: ")
        if prompt.lower() in ["exit", "quit"]:
            break
        reply = chat(prompt)
        print("AI:", reply)
