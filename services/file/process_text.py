import uuid
import logging
from utils.file.semantic_chunking import get_semantic_chunking
from utils.chatbot.load_embeddings import load_hugging_face_embeddings
from services.milvus.store import MilvusVectorStore


def process_txt(
    raw_text: str,
    embedding_model_name: str,
    chunk_size: int = None,
    same_vectorstore: bool = False,
    collection_name: str = None,
    index_params: dict = None,
):
    embeddings = load_hugging_face_embeddings(embedding_model_name)

    semantic_documents = get_semantic_chunking(raw_text, embeddings)
    texts = [doc.page_content for doc in semantic_documents]
    vectors = embeddings.embed_documents(texts)
    ids = [str(uuid.uuid4()) for _ in texts]

    store = MilvusVectorStore(collection_name="test_collection")

    try:
        if not same_vectorstore:
            vector_dim = len(vectors[0])
            store.create_collection(
                dim=vector_dim,
                index_params=index_params
                or {
                    "metric_type": "L2",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128},
                },
            )

        store.add_texts(texts=texts, vectors=vectors)
        return True
    except Exception as e:
        logging.error(f"[Milvus] Error: {e}")
        return None
