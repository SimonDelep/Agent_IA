import os
import chromadb
import openai

from config import (
    OPENAI_API_KEY,
    OPENAI_ENDPOINT,
    OPENAI_API_VERSION,
    OPENAI_EMBEDDING_MODEL,
    CHROMA_PATH,
    CHROMA_COLLECTION,
)
from utils import load_pdf_text, clean_text, chunk_text

client = openai.AzureOpenAI(
    azure_endpoint=OPENAI_ENDPOINT,
    api_key=OPENAI_API_KEY,
    api_version=OPENAI_API_VERSION
)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(
    name=CHROMA_COLLECTION
)

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding

def ingest_pdf(pdf_path: str) -> None:
    raw_text = load_pdf_text(pdf_path)
    cleaned_text = clean_text(raw_text)
    chunks = chunk_text(cleaned_text, chunk_size=800, overlap=120)

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    filename = os.path.basename(pdf_path)

    for i, chunk in enumerate(chunks):
        chunk_id = f"{filename}_chunk_{i}"
        embedding = get_embedding(chunk)

        ids.append(chunk_id)
        documents.append(chunk)
        embeddings.append(embedding)
        metadatas.append({
        "source": filename,
        "chunk_index": i
    })

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(f"Ingestion terminée : {len(chunks)} chunks ajoutés.")

if __name__ == "__main__":
    ingest_pdf("./data/68DC4985C2124.pdf")
