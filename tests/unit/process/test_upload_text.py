import pytest
from unittest.mock import patch
from fastapi import HTTPException
from tests.conftest import client

from main import app
from db.models.chatbot.chatbot import Chatbot
from core.security import verify_api_key


@pytest.fixture
def headers():
    return {"X-API-Key": "test"}


@pytest.fixture
def valid_text_input():
    return {
        "chatbot_id": 1,
        "file_name": "test_text",
        "text": "This is a test text content",
    }


def reset_overrides():
    app.dependency_overrides.clear()


@patch("api.v1.process.routes.upload.upload_text.embedding_pipeline")
@patch("api.v1.process.routes.upload.upload_text.create_data_source")
def test_successful_text_upload(
    mock_create_data_source,
    mock_embedding,
    db_session,
    client,
    headers,
    valid_text_input,
):
    chatbot = Chatbot(name="TestBot", description="test description")
    db_session.add(chatbot)
    db_session.commit()

    response = client.post("/process/text", json=valid_text_input, headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "message": "Text uploaded successfully",
        "chatbot_id": 1,
        "file_name": "test_text",
        "text": valid_text_input["text"],
    }


def test_text_upload_without_authentication(client, valid_text_input):
    response = client.post("/process/text", json=valid_text_input)
    assert response.status_code == 403


@patch("core.security.verify_api_key")
def test_text_upload_with_invalid_api_key(
    mock_verify_api_key, client, valid_text_input
):
    mock_verify_api_key.side_effect = HTTPException(
        status_code=401, detail="Invalid API key"
    )

    headers = {"X-API-Key": "invalid_key"}
    response = client.post("/process/text", json=valid_text_input, headers=headers)

    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]


def test_text_upload_with_nonexistent_chatbot(db_session, client, headers):
    invalid_input = {
        "chatbot_id": 99999,
        "file_name": "test_text",
        "text": "This is a test text content",
    }

    response = client.post("/process/text", json=invalid_input, headers=headers)

    assert response.status_code == 404
    assert "Chatbot not found" in response.json()["detail"]
