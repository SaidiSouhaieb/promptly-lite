import uuid


from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility,
)
from sentence_transformers import SentenceTransformer
from langchain.schema import Document


class MilvusVectorStore:
    def __init__(
        self,
        collection_name: str,
        dim: int = 768,
        host="milvus-standalone",
        port="19530",
    ):
        self.collection_name = collection_name
        self.dim = dim
        self.embedding_field = "embedding"
        self.text_field = "text"
        self.id_field = "id"

        connections.connect("default", host=host, port=port)

        self.collection = None
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            self.collection.load()

    def _ensure_collection(self):
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            self.collection.load()
            return

        fields = [
            FieldSchema(
                name=self.id_field,
                dtype=DataType.VARCHAR,
                is_primary=True,
                auto_id=False,
                max_length=36,
            ),
            FieldSchema(name=self.text_field, dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(
                name=self.embedding_field, dtype=DataType.FLOAT_VECTOR, dim=self.dim
            ),
        ]

        schema = CollectionSchema(fields, description="Promptly user documents")
        self.collection = Collection(name=self.collection_name, schema=schema)
        self.collection.create_index(
            self.embedding_field,
            {"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 128}},
        )
        self.collection.load()

    def create_collection(self, dim: int, index_params: dict = None):
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)

        fields = [
            FieldSchema(
                name=self.id_field,
                dtype=DataType.VARCHAR,
                is_primary=True,
                auto_id=False,
                max_length=36,
            ),
            FieldSchema(name=self.text_field, dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(
                name=self.embedding_field, dtype=DataType.FLOAT_VECTOR, dim=dim
            ),
        ]

        schema = CollectionSchema(fields, description="Promptly user documents")
        self.collection = Collection(name=self.collection_name, schema=schema)

        self.collection.create_index(
            self.embedding_field,
            index_params
            or {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128},
            },
        )
        self.collection.load()

    def add_texts(self, texts, vectors=None):
        if vectors is None:
            raise ValueError("Embeddings must be provided externally")

        ids = [str(uuid.uuid4()) for _ in texts]
        data = [ids, texts, vectors]
        self.collection.insert(data)

    def similarity_search(self, query_embedding, top_k=5):
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

        results = self.collection.search(
            data=[query_embedding],
            anns_field=self.embedding_field,
            param=search_params,
            limit=top_k,
            output_fields=[self.text_field],
        )

        hits = results[0]
        for hit in hits:
            print(f"type: {type(hit['entity']['text'])}")

        documents = []
        for hit in hits:
            text = hit["entity"].get("text", "")
            if isinstance(text, Document):
                text = text.page_content
            elif not isinstance(text, str):
                text = str(text)
            documents.append(
                Document(
                    page_content=text,
                    metadata={"id": hit["id"], "distance": hit["distance"]},
                )
            )

        return documents
