import os
import shutil
from typing import Optional, List, Annotated

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Body,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session
from pydantic import BaseModel


from db.models.file.data_source import DataSource
from db.models.chatbot import Chatbot
from models.file.text_input import ProcessInput
from db.session import get_db
from services.file.embedding_pipeline import embedding_pipeline
from services.file.upload import create_data_source
from services.file.content_extractor import ExtractContent
from models.file.qa_input import QARequest
from models.file.upload_response import UploadTextResponse
from core.constants import STORAGE_PATH, EMBEDDING_MODEL_NAME
from core.logging import logging
from utils.file.path_utils import get_semantic_folder_path
from core.security import verify_api_key

process_router = APIRouter(prefix="")
content_extractor = ExtractContent()


@process_router.post("/text", response_model=UploadTextResponse)
async def process_text_input(
    input: ProcessInput,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    chatbot = db.query(Chatbot).filter(Chatbot.id == input.chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    vector_store_path = get_semantic_folder_path(input.file_name)
    same_vectorstore = os.path.exists(vector_store_path)

    embedding_pipeline(
        EMBEDDING_MODEL_NAME, input.text.lower(), vector_store_path, same_vectorstore
    )

    create_data_source(
        file_name=input.file_name,
        file_type="txt",
        file_path=vector_store_path,
        chatbot_id=input.chatbot_id,
        db=db,
    )
    return {
        "message": "Text uploaded successfully",
        "chatbot_id": input.chatbot_id,
        "file_name": input.file_name,
        "text": input.text,
    }
