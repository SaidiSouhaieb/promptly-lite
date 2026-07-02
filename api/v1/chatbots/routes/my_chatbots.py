from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.models.chatbot import Chatbot
from db.session import get_db
from models.chatbot.my_chatbots import MyChatbotsResponse, Chatbot as ChatbotModel
from core.security import verify_api_key


my_chatbots_router = APIRouter(prefix="/my-chatbots")


@my_chatbots_router.post("/", response_model=MyChatbotsResponse)
async def my_chatbots_endpoint(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    chatbots = db.query(Chatbot.name, Chatbot.description).all()

    if not chatbots:
        raise HTTPException(status_code=404, detail="No chatbots found for the user.")

    response_chatbots = [
        ChatbotModel(name=chatbot.name, description=chatbot.description)
        for chatbot in chatbots
    ]

    return MyChatbotsResponse(chatbots=response_chatbots)
