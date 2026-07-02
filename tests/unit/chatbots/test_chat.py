import pytest
from tests.conftest import client
from fastapi import HTTPException
from unittest.mock import patch, AsyncMock
from main import app

from db.models.chatbot.chatbot import Chatbot
from api.v1.chatbots.routes.chat import verify_api_key


@pytest.fixture
def headers():
    return {"X-API-Key": "test"}


@pytest.fixture
def chat_input():
    return {
        "chatbot_id": 1,
        "text": "Hello, how are you?",
        "model_name": "mistral7b",
    }


def reset_overrides():
    app.dependency_overrides.clear()


@patch("api.v1.chatbots.routes.chat.get_chatbot_and_data_source")
@patch("api.v1.chatbots.routes.chat.generate_response", new_callable=AsyncMock)
def test_successful_chat(
    mock_generate_response, mock_get_data, client, db_session, headers, chat_input
):
    chatbot = Chatbot(name="TestBot", description="test description")
    db_session.add(chatbot)
    db_session.commit()

    mock_get_data.return_value = (chatbot, object())
    mock_generate_response.return_value = "Mocked reply"

    response = client.post("/chatbots/chat", json=chat_input, headers=headers)
    print(response.json(), "respopnse'n\n")

    assert response.status_code == 200
    assert response.json()["reply"] == "Mocked reply"
    reset_overrides()


def test_chat_without_authentication(client, chat_input):
    response = client.post("/chatbots/chat", json=chat_input)
    assert response.status_code == 403


@patch("core.security.verify_api_key")
def test_chat_with_invalid_api_key(mock_verify_api_key, client, chat_input):
    mock_verify_api_key.side_effect = HTTPException(
        status_code=401, detail="Invalid API key"
    )

    headers = {"X-API-Key": "invalid_key"}
    response = client.post("/chatbots/chat", json=chat_input, headers=headers)

    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]


@patch("api.v1.chatbots.routes.chat.get_chatbot_and_data_source")
def test_chat_with_nonexistent_chatbot(mock_get_data, client, headers, chat_input):
    mock_get_data.side_effect = HTTPException(
        status_code=404, detail="Chatbot not found"
    )

    response = client.post("/chatbots/chat", json=chat_input, headers=headers)

    assert response.status_code == 404
    assert "Chatbot not found" in response.json()["detail"]
    reset_overrides()


@patch("api.v1.chatbots.routes.chat.get_chatbot_and_data_source")
@patch("api.v1.chatbots.routes.chat.generate_response", new_callable=AsyncMock)
def test_chat_with_generation_error(
    mock_generate_response, mock_get_data, client, headers, db_session, chat_input
):

    chatbot = Chatbot(name="TestBot", description="test description")
    db_session.add(chatbot)
    db_session.commit()

    mock_get_data.return_value = (chatbot, object())
    mock_generate_response.return_value = "Mocked reply"
    mock_get_data.side_effect = HTTPException(
        status_code=404, detail="Failed to generate response"
    )

    response = client.post("/chatbots/chat", json=chat_input, headers=headers)

    assert response.status_code == 404
    assert "Failed to generate response" in response.json()["detail"]
    reset_overrides()
