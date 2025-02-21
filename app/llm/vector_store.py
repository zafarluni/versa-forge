# This file provides abstractions for interacting with vector stores.

from app.services.vector_store_service import BaseVectorStore, DummyVectorStore

# For now, we can instantiate a dummy vector store.
vector_store = DummyVectorStore()

def add_document_to_store(document: dict) -> None:
    vector_store.add_document(document)

def query_vector_store(query: str, top_k: int = 5):
    return vector_store.query(query, top_k)
