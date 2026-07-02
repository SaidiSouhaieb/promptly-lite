import os
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.chatbot.text_input import TextInput
from db.models.chatbot import Chatbot
from db.models.file.data_source import DataSource
from db.session import get_db
from llms.loaders.model_loader import ModelLoader
from services.chatbot.get_chain import get_chain
from core.security import verify_api_key


my_data_sources_router = APIRouter(prefix="/my-data-sources")

model_loader = ModelLoader()


@my_data_sources_router.post("/{chatbot_id}")
async def my_data_sources_endpoint(
    db: Session = Depends(get_db),
    chatbot_id: str = "",
    api_key: str = Depends(verify_api_key),
):
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot:
        return {"error": "Chatbot not found"}

    data_sources = (
        db.query(DataSource).filter(DataSource.chatbot_id == chatbot_id).all()
    )
    return data_sources
