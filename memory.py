import chromadb
from langchain_openai import OpenAIEmbeddings
import uuid
import numpy as np

client = chromadb.PersistentClient("vector_db")
collection = client.get_or_create_collection("chat_memory")

embedding_model = OpenAIEmbeddings()


def embed(text):
    return embedding_model.embed_query(text)


def store_memory(text, memory_type="general"):
    collection.add(
        documents=[text],
        embeddings=[embed(text)],
        metadatas=[{"type": memory_type}],
        ids=[str(uuid.uuid4())],
    )


def retrieve_memory(query, top_k=3):
    results = collection.query(query_embeddings=[embed(query)], n_results=top_k)
    return results["documents"][0] if results["documents"] else []

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def is_duplicate(new_memory, threshold=0.85):
    new_embedding = embed(new_memory)

    results = collection.query(
        query_embeddings=[new_embedding],
        n_results=3,
        include=["embeddings", "documents"]
    )

    if not results["embeddings"] or len(results["embeddings"][0]) == 0:
        return False

    for i, existing_embedding in enumerate(results["embeddings"][0]):
        score = cosine_similarity(new_embedding, existing_embedding)

        print(f"Similarity: {score:.3f} | Existing: {results['documents'][0][i]}")

        if score > threshold:
            return True

    return False

def update_memory(new_memory, memory_type, threshold=0.75):
    new_embedding = embed(new_memory)

    results = collection.query(
        query_embeddings=[new_embedding],
        n_results=5,
        include=["embeddings", "metadatas"]
    )

    if not results["ids"] or len(results["ids"][0]) == 0:
        return False

    for i in range(len(results["ids"][0])):
        existing_embedding = results["embeddings"][0][i]
        metadata = results["metadatas"][0][i]

        score = cosine_similarity(new_embedding, existing_embedding)

        if score > threshold and metadata["type"] == memory_type:
            old_id = results["ids"][0][i]

            collection.delete(ids=[old_id])
            store_memory(new_memory, memory_type)

            print(f"🔄 Updated memory (similarity: {score:.3f})")
            return True

    return False