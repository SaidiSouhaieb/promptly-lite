import os

from services.file.process_text import process_txt
import logging


def embedding_pipeline(
    embedding_model,
    raw_text,
    vector_store_path,
    same_vectorstore=False,
    chunk_size=1000,
):
    os.makedirs(vector_store_path, exist_ok=True)
    process_txt(
        raw_text=raw_text,
        embedding_model_name=embedding_model,
        chunk_size=chunk_size,
        collection_name=vector_store_path,
        same_vectorstore=same_vectorstore,
    )

    logging.info(f"Processing complete. Vector store saved to '{vector_store_path}'.")
