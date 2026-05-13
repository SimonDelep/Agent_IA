import chromadb
from openai import AzureOpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_ENDPOINT,
    OPENAI_API_VERSION,
    OPENAI_EMBEDDING_MODEL,
    CHROMA_PATH,
    CHROMA_COLLECTION,
)

client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    api_version=OPENAI_API_VERSION,
    azure_endpoint=OPENAI_ENDPOINT,
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

def search(query: str, top_k: int = 3):
    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results

if __name__ == "__main__":
    question = "Qu'est-ce qu'un agent dans un système d'orchestration ?"
    results = search(question, top_k=3)

    for i, doc in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        print("-" * 80)
        print(f"Source : {metadata}")
        print(doc)

