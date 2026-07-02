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
from services.file.content_extractor import ExtractContent
from utils.file.remove_file_extensions import get_file_type
from core.constants import EMBEDDING_MODEL_NAME, STORAGE_PATH
from core.logging import logging


def create_data_source(file_name, file_type, file_path, chatbot_id, db):
    data_source = DataSource(
        name=file_name,
        type=file_type,
        file_path=file_path,
        chatbot_id=chatbot_id,
    )
    try:
        db.add(data_source)
        db.commit()
        db.refresh(data_source)
    except Exception as e:
        db.rollback()
        logging.error(f"File uploading failed: {e}")
        raise Exception("File uploading failed") from e
