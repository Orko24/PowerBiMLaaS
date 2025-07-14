from transformers import pipeline
import os

hf_token = "token here"

generator = pipeline(
    "text-generation",
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=hf_token
)

prompt = "You are a data scientist. Given columns: ['job_id', 'title', 'description', 'fraudulent'], generate pandas code to clean it into a fraud detection format."

result = generator(prompt, max_new_tokens=200, do_sample=True, temperature=0.7)
print(result[0]["generated_text"])
