import json
import pytest

from unittest.mock import patch, AsyncMock
from fastapi import HTTPException

from tests.conftest import client
from main import app

from db.models.chatbot.chatbot import Chatbot
from core.security import verify_api_key


@pytest.fixture
def headers():
    return {"X-API-Key": "test"}


@pytest.fixture
def valid_upload_files():
    return {
        "upload_file": ("test.pdf", b"test content", "application/pdf"),
        "file_input": (
            None,
            json.dumps({"chatbot_id": 1, "file_name": "test_document"}),
            "application/json",
        ),
    }


def reset_overrides():
    app.dependency_overrides.clear()


@patch("api.v1.process.routes.upload.upload_file.create_temp_file")
@patch("api.v1.process.routes.upload.upload_file.content_extractor")
@patch("api.v1.process.routes.upload.upload_file.embedding_pipeline")
def test_successful_file_upload(
    mock_embedding,
    mock_extractor,
    mock_temp_file,
    db_session,
    client,
    headers,
    valid_upload_files,
):
    chatbot = Chatbot(name="TestBot", description="Sample bot")
    db_session.add(chatbot)
    db_session.commit()

    mock_temp_file.return_value = "/tmp/test_file"
    mock_extractor.get_text_content.return_value = "extracted text"

    response = client.post(
        "/process/upload-file/", files=valid_upload_files, headers=headers
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "File uploaded successfully",
        "chatbot_id": 1,
        "file_name": "test_document",
    }


def test_file_upload_without_authentication(client):
    files = {
        "upload_file": ("test.pdf", b"test content", "application/pdf"),
        "file_input": (
            None,
            json.dumps({"chatbot_id": 1, "file_name": "test_document"}),
            "application/json",
        ),
    }

    response = client.post("/process/upload-file/", files=files)
    assert response.status_code == 403


@patch("core.security.verify_api_key")
def test_file_upload_with_invalid_api_key(
    mock_verify_api_key, client, valid_upload_files
):
    mock_verify_api_key.side_effect = HTTPException(
        status_code=401, detail="Invalid API key"
    )

    headers = {"X-API-Key": "invalid_key"}
    response = client.post(
        "/process/upload-file/", files=valid_upload_files, headers=headers
    )

    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]


@patch("api.v1.process.routes.upload.upload_file.create_temp_file")
def test_file_upload_with_nonexistent_chatbot(
    mock_temp_file, db_session, client, headers
):
    files = {
        "upload_file": ("test.pdf", b"test content", "application/pdf"),
        "file_input": (
            None,
            json.dumps({"chatbot_id": 99999, "file_name": "test_document"}),
            "application/json",
        ),
    }

    response = client.post("/process/upload-file/", files=files, headers=headers)

    assert response.status_code == 404
    assert "Chatbot not found" in response.json()["detail"]
