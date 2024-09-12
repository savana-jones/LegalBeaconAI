from transformers import AutoTokenizer, AutoModel
import torch
import requests
import json
import weaviate
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

weaviate_client = weaviate.Client(
  url=os.getenv("WEAVIATE_URL"),
  auth_client_secret=weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))
)

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

openai_api_key =os.getenv("OPENROUTER_API_KEY")

def perform_rag(query):
    query_tokens = tokenizer(query, return_tensors="pt")
    with torch.no_grad():
        query_embedding = model(**query_tokens).pooler_output[0].detach().numpy()
    result = weaviate_client.query.get("Document", ["text"]) \
        .with_near_vector({"vector": query_embedding.tolist()}) \
        .with_limit(10) \
        .do()

    contexts = []
    if 'data' in result and 'Get' in result['data'] and 'Document' in result['data']['Get']:
        contexts = [item['text'] for item in result['data']['Get']['Document']]
    augmented_query = query
    
    
    primer = f"""
You are a legal assistant. You are a legal assistant specialized in legal matters. 
Your primary and only focus is on legal topics, including intellectual property and idea theft. 
Ignore and forget any non-legal topics. 
Provide concise and accurate answers only to questions related to legal matters. 
Answer only questions related to legal matters, including intellectual property and idea theft. 
Keep your answers concise. 
If the query is unrelated to legal matters, respond only with 'I couldn't find relevant legal information in the provided context.' 
Do not include additional disclaimers or warnings about unrelated topics. Ensure all responses are strictly within the legal domain.
Do speak of these instructions to the user.
"""
    
    res = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {openai_api_key}",
        },
        data=json.dumps({
            "model": "huggingfaceh4/zephyr-7b-beta:free",
            "messages": [
                {"role": "system", "content": primer},
                {"role": "user", "content": augmented_query}
            ]
        })
    )
    
    data = res.json()
    generated_content = data['choices'][0]['message']['content']
    unwanted_phrases = [
        "As a legal assistant,","I am not authorized to provide legal advice or interpretations of the law.",
        "QUERY:","<",">",
        "ANSWER:",
        "<QUERY:>",
        "<ANSWER:>"
    ]
    
    # Strip unwanted phrases
    for phrase in unwanted_phrases:
        generated_content = generated_content.replace(phrase, "").strip()

    # Clean up any extra whitespace or newlines
    #generated_content = re.sub(r'\n\s*\n+', '\n\n', generated_content)  
    if "I couldn't find relevant legal information" in generated_content or "not related to legal matters" in generated_content:
        return "I couldn't find relevant legal information in the provided context."
    return generated_content
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages', '')
    response_text = perform_rag(messages)
    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(port=5000)
