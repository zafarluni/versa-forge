from abc import ABC, abstractmethod
from typing import List, Any

class BaseVectorStore(ABC):
    @abstractmethod
    def add_document(self, document: Any) -> None:
        pass

    @abstractmethod
    def query(self, query_text: str, top_k: int) -> List[Any]:
        pass

# Example implementation for a vector store backend (e.g., Milvus, Qdrant)
class DummyVectorStore(BaseVectorStore):
    def __init__(self):
        self.documents = []

    def add_document(self, document: Any) -> None:
        self.documents.append(document)

    def query(self, query_text: str, top_k: int) -> List[Any]:
        # Dummy implementation that returns first top_k documents
        return self.documents[:top_k]
