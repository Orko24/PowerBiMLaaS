from transformers import AutoTokenizer, AutoModelForCausalLM

# Make sure this token is loaded in your environment
# or passed as use_auth_token="your_token_here" in both calls

token = "throw in token here"

tokenizer = AutoTokenizer.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2", use_auth_token=token
)
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2", use_auth_token=token
)
