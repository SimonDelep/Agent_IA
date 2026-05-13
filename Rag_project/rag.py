import chromadb
from openai import AzureOpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_ENDPOINT,
    OPENAI_API_VERSION,
    OPENAI_EMBEDDING_MODEL,
    OPENAI_CHAT_MODEL,
    CHROMA_PATH,
    CHROMA_COLLECTION
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

def retrieve_context(query: str, top_k: int = 3):
    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    context_blocks = []
    sources = []

    for doc, meta in zip(docs, metas):
        context_blocks.append(doc)
        sources.append(meta)

    return "\n\n".join(context_blocks), sources

def answer_with_rag(question: str) -> dict:
    context, sources = retrieve_context(question, top_k=3)
    prompt = f"""
Tu es un assistant académique.
Réponds uniquement à partir du contexte ci-dessous.
S'il l'information manque, indique-le clairement.

Contexte :
{context}

Question :
{question}
"""

    response = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": "Tu réponds dans un style formel, clair et précis."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": sources
    }

if __name__ == "__main__":
    question = "Explique le rôle d'une base vectorielle dans un système RAG."
    result = answer_with_rag(question)

    print("\nREPONSE\n")
    print(result["answer"])
    print("\nSOURCES\n")
    for source in result["sources"]:
        print(source)