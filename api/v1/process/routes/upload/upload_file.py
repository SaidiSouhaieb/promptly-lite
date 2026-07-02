import os
import shutil
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Form, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from tempfile import NamedTemporaryFile

from models.file.file_input import FileInput
from db.models.file.data_source import DataSource
from db.models.chatbot import Chatbot
from db.session import get_db
from services.file.embedding_pipeline import embedding_pipeline
from services.file.upload import create_data_source
from services.file.content_extractor import ExtractContent
from services.chatbot.chat import generate_response, get_chatbot_and_data_source
from models.file.upload_response import UploadResponse
from utils.file.remove_file_extensions import get_file_type
from utils.file.create_temp_file import create_temp_file
from utils.file.path_utils import get_semantic_folder_path
from core.constants import STORAGE_PATH, EMBEDDING_MODEL_NAME
from core.logging import logging
from core.security import verify_api_key

process_router = APIRouter(prefix="")
content_extractor = ExtractContent()


@process_router.post("/upload-file/", response_model=UploadResponse)
async def process_file_upload(
    file_input: Annotated[FileInput, Body(...)],
    upload_file: Annotated[UploadFile, File(...)],
    db: Annotated[Session, Depends(get_db)],
    api_key: str = Depends(verify_api_key),
):
    chatbot = db.query(Chatbot).filter(Chatbot.id == file_input.chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    temp_path = create_temp_file(upload_file)

    try:
        raw_text = content_extractor.get_text_content(temp_path)
        file_type = get_file_type(upload_file.filename)

        vector_store_path = get_semantic_folder_path(file_input.file_name)
        same_vectorstore = os.path.exists(vector_store_path)

        embedding_pipeline(
            EMBEDDING_MODEL_NAME, raw_text.lower(), vector_store_path, same_vectorstore
        )
        create_data_source(
            file_name=file_input.file_name,
            file_type=file_type,
            file_path=vector_store_path,
            chatbot_id=file_input.chatbot_id,
            db=db,
        )

        return {
            "message": "File uploaded successfully",
            "chatbot_id": file_input.chatbot_id,
            "file_name": file_input.file_name,
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
