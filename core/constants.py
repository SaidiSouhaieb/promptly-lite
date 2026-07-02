# API Response Constants
SUCCESS = "Success"
FAILURE = "Failure"
INVALID_USER_ID = "User ID must be a positive integer"
FILE_NOT_FOUND = "The file was not found"
EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

# Storage
STORAGE_PATH = "storage"
TEMP_PATH = "temp"


# Embedding
EMBEDDING_MODEL_NAME = "Sahajtomar/french_semantic"

# Chroma Settings
CHROMA_CLIENT_SETTINGS = {
    "anonymized_telemetry": False,
    "is_persistent": True,
}
