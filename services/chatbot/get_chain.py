import os

from sentence_transformers import SentenceTransformer


from llms.loaders.model_loader import ModelLoader
from llms.prompts.load_prompt import load_prompt
from utils.chatbot.load_db import load_db
from utils.chatbot.load_qa_chain import RetrievalQAChain
from services.milvus.retriever import MilvusRetriever
from services.milvus.store import MilvusVectorStore


model_loader = ModelLoader()


from utils.chatbot.load_qa_chain import RetrievalQAChain


def get_chain(db_path, embedding_model_name, model_name, query):
    llm = model_loader.load_model(model_name)
    prompt = load_prompt(model_name)
    embedding_model = SentenceTransformer(embedding_model_name)
    vector_store = MilvusVectorStore(
        collection_name="test_collection",
        dim=embedding_model.get_sentence_embedding_dimension(),
    )

    retriever = MilvusRetriever(
        milvus_store=vector_store,
        embeddings=embedding_model,
        k=5,
    )

    qa_chain = RetrievalQAChain(
        llm=llm, prompt=prompt, db=vector_store, query=query, retriever=retriever
    )
    return qa_chain
