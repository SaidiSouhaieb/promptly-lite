from langchain.schema import BaseRetriever, Document
from pydantic import Field
from typing import Any


class MilvusRetriever(BaseRetriever):
    milvus_store: Any = Field(...)
    embeddings: Any = Field(...)
    k: int = Field(default=5)

    def get_relevant_documents(self, query: str) -> list[Document]:
        query_embedding = self.embeddings.encode(query)
        texts = self.milvus_store.similarity_search(query_embedding, top_k=self.k)
        return texts
