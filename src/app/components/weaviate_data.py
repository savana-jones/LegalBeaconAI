"""from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from llama_index.llms.openrouter import OpenRouter
import tiktoken"""
from transformers import AutoTokenizer, AutoModel
import torch
import requests
import json
import weaviate
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

auth_config = weaviate.AuthApiKey(api_key="3wtFyyjyllyt1LVCkDZ8LxhjjNMaA1RmJ7Jj")
openai_api_key = "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"
weaviate_client = weaviate.Client(
  url="https://knxspjmsraya6c6ylu76q.c0.us-east1.gcp.weaviate.cloud",
  auth_client_secret=auth_config
)
"""
host="https://legalchatbot-no85g3l.svc.aped-4627-b74a.pinecone.io"
schema = {
    "classes": [
        {
            "class": "LegalDocument",
            "properties": [
                {
                    "name": "text",
                    "dataType": ["text"]
                },
                {
                    "name": "embedding",
                    "dataType": ["number[]"]
                }
            ]
        }
    ]
}

# Create schema in Weaviate
weaviate_client.schema.create(schema)

loader = PyPDFLoader("C:/Users/DELL/Downloads/GPO-CONAN-REV-2016.pdf")
data = loader.load()
tokenizer = tiktoken.get_encoding('p50k_base')
print("1")
def tiktoken_len(text):
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=100,
    length_function=tiktoken_len,
    separators=["\n\n", "\n", " ", ""]
)
print("2")
texts = [doc.page_content for doc in text_splitter.split_documents(data)]
print("3")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Store embeddings in Weaviate
for text in texts:
    embedding = embeddings.embed_query(text)  # Assuming you have an embed method in your embeddings object
    weaviate_client.data_object.create(
        {
            "text": text,
            "embedding": embedding # Convert to list if numpy array
        },
        class_name="LegalDocument"
    )
print("4")

pinecone_api_key = "54d7a80e-5a4e-44b3-a96b-b391d24b7d72"
os.environ['PINECONE_API_KEY'] = pinecone_api_key
"""
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/roberta-base-nli-stsb-mean-tokens")
model = AutoModel.from_pretrained("sentence-transformers/roberta-base-nli-stsb-mean-tokens")


# Check the schema
schema = weaviate_client.schema.get()
def perform_rag(query):
    query_tokens = tokenizer(query, return_tensors="pt")
    with torch.no_grad():
        query_embedding = model(**query_tokens).pooler_output[0].detach().numpy()
    result = weaviate_client.query.get("LegalDocument", ["text"]) \
        .with_near_vector({"vector": query_embedding.tolist()}) \
        .with_limit(10) \
        .do()
    #print("Weaviate Query Result:", result)

    contexts = []
    if 'data' in result and 'Get' in result['data'] and 'LegalDocument' in result['data']['Get']:
        contexts = [item['text'] for item in result['data']['Get']['LegalDocument']]
    #print("Context:",contexts)
    augmented_query = "<CONTEXT>\n" + "\n\n-------\n\n".join(contexts) + "\n-------\n</CONTEXT>\n\n\n\nMY QUESTION:\n" + query
    
    primer = f"""You are an expert lawyer. Answer any questions I have about legal matters and forget everything other than the legal matters and law. If the query provided does not ask about legal matters , respond with 'I couldn't find relevant information in the provided context.' You always answer questions based only on the context that you have been provided.
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
    if "I don't know" in generated_content or "I'm not sure" in generated_content or "couldn't find" in generated_content:
        return "I couldn't find relevant information in the provided context."
    return generated_content
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages', '')
    response_text = perform_rag(messages)
    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(port=5000)