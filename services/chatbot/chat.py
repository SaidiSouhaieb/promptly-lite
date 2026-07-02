import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from models.chatbot.text_input import TextInput
from db.models.file.data_source import DataSource
from db.models.chatbot.chatbot import Chatbot

from services.chatbot.get_chain import get_chain
from core.constants import EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)


def get_chatbot_and_data_source(db: Session, chatbot_id: str):
    chatbot = (
        db.execute(select(Chatbot).where(Chatbot.id == chatbot_id)).scalars().first()
    )
    if not chatbot:
        raise ValueError("Chatbot not found")

    data_source = (
        db.execute(select(DataSource).where(DataSource.chatbot_id == chatbot.id))
        .scalars()
        .first()
    )

    print("data_source", data_source)
    if not data_source:
        raise ValueError("Data source not found")

    return chatbot, data_source


async def generate_response(input: TextInput, data_source: DataSource):
    qa_chain = get_chain(
        data_source.file_path,
        EMBEDDING_MODEL_NAME,
        input.model_name,
        input.text,
    )
    try:
        response = await run_in_threadpool(qa_chain.invoke, input.text)
    except Exception:
        logger.exception("QA chain failed.")
        raise Exception("LLM failed") from e

    return response


#
