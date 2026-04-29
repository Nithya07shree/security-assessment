"""
RAG pipeline
data for seeding stored in ai-service/data
data after seeding (embeddings) stored in ai-service/chroma_data 

for first timers:
    start flask application: python app.py
    data gets embedded automatically into your local storage. (Do not commit this to github) add chroma_data to gitignore.

for testing RAG pipeline:
    execute the /query endpoint. refer to the respective file for execution instructions
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_data")

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = client.get_or_create_collection(
    name="security_docs"
)

def load_document():
    path = os.path.join(DATA_DIR, "security_docs.txt")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks

def seed_collection():
    if collection.count() > 0:
        return

    text = load_document()
    chunks = chunk_text(text)

    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()

        collection.add(
            ids=[f"chunk_{i}"],
            documents=[chunk],
            embeddings=[embedding]
        )

def query_docs(question, top_k=3):
    embedding = model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    return results