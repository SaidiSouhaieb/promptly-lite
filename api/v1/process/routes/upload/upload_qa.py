import os
import shutil
from typing import Annotated

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
from typing import Optional, List
from pydantic import BaseModel
from tempfile import NamedTemporaryFile

from models.file.qa_input import QARequest
from db.models.file.data_source import DataSource
from db.models.chatbot import Chatbot
from db.session import get_db
from services.file.embedding_pipeline import embedding_pipeline
from services.file.upload import create_data_source
from models.file.upload_response import UploadQAResponse
from utils.file.path_utils import get_semantic_folder_path
from core.constants import EMBEDDING_MODEL_NAME
from core.logging import logging
from core.security import verify_api_key

process_router = APIRouter(prefix="")


@process_router.post("/qa", response_model=UploadQAResponse)
async def process_qa_list(
    input: Annotated[QARequest, Body(...)],
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    chatbot = db.query(Chatbot).filter(Chatbot.id == input.chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    combined_text = "\n\n".join(
        [f"Question: {qa.question}\nAnswer: {qa.answer}" for qa in input.qa_list]
    )

    vector_store_path = get_semantic_folder_path(input.file_name)
    same_vectorstore = os.path.exists(vector_store_path)

    embedding_pipeline(
        EMBEDDING_MODEL_NAME, combined_text.lower(), vector_store_path, same_vectorstore
    )

    create_data_source(
        file_name=input.file_name,
        file_type="qa",
        file_path=vector_store_path,
        chatbot_id=input.chatbot_id,
        db=db,
    )

    return {
        "message": "File uploaded successfully",
        "chatbot_id": input.chatbot_id,
        "file_name": input.file_name,
        "qa_list": input.qa_list,
    }
