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
def valid_qa_input():
    return {
        "chatbot_id": 1,
        "file_name": "test_qa",
        "qa_list": [
            {"question": "Test question 1?", "answer": "Test answer 1"},
            {"question": "Test question 2?", "answer": "Test answer 2"},
        ],
    }


def reset_overrides():
    app.dependency_overrides.clear()


@patch("api.v1.process.routes.upload.upload_qa.embedding_pipeline")
@patch("api.v1.process.routes.upload.upload_qa.create_data_source")
def test_successful_qa_upload(
    mock_create_data_source,
    mock_embedding,
    db_session,
    client,
    headers,
    valid_qa_input,
):
    chatbot = Chatbot(name="TestBot", description="test description")
    db_session.add(chatbot)
    db_session.commit()

    response = client.post("/process/qa", json=valid_qa_input, headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "message": "File uploaded successfully",
        "chatbot_id": 1,
        "file_name": "test_qa",
        "qa_list": valid_qa_input["qa_list"],
    }


def test_qa_upload_without_authentication(client, valid_qa_input):
    response = client.post("/process/qa", json=valid_qa_input)
    assert response.status_code == 403


@patch("core.security.verify_api_key")
def test_qa_upload_with_invalid_api_key(mock_verify_api_key, client, valid_qa_input):
    mock_verify_api_key.side_effect = HTTPException(
        status_code=401, detail="Invalid API key"
    )

    headers = {"X-API-Key": "invalid_key"}
    response = client.post("/process/qa", json=valid_qa_input, headers=headers)

    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]


def test_qa_upload_with_nonexistent_chatbot(db_session, client, headers):
    qa_input = {
        "chatbot_id": 99999,
        "file_name": "test_qa",
        "qa_list": [{"question": "Test question?", "answer": "Test answer"}],
    }

    response = client.post("/process/qa", json=qa_input, headers=headers)

    assert response.status_code == 404
    assert "Chatbot not found" in response.json()["detail"]
