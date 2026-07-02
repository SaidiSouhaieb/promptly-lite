from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel

from models.chatbot.text_input import TextInput
from db.models.chatbot import Chatbot
from db.session import get_db
from core.security import verify_api_key

from services.chatbot.chat import generate_response, get_chatbot_and_data_source
from models.chatbot.chat_response import ChatResponse

chatbot_router = APIRouter(prefix="/chat")


@chatbot_router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    input: TextInput,
    db: Annotated[Session, Depends(get_db)],
    api_key: str = Depends(verify_api_key),
):
    chatbot = db.query(Chatbot).filter(Chatbot.id == input.chatbot_id).first()
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found"
        )

    chatbot, data_source = get_chatbot_and_data_source(db, input.chatbot_id)

    try:
        reply = await generate_response(input, data_source)
        return ChatResponse(reply=reply)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
