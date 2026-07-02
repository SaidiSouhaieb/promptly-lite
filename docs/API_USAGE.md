
# Promptly API Usage Guide

## Before You Begin

Make sure you have the Promptly backend installed and running by following the [Installation](../README.md#installation) instructions in the main README.

- You should have the server running locally or deployed, with the backend accessible at `http://localhost:3000` (or your configured port).
- Set your `API_KEY` in your request headers for authentication.
- You need at least one chatbot created before uploading data or querying.

---

## Authentication

All API requests require an `x-api-key` header with your API key:

```
x-api-key: YOUR_API_KEY
```

---

## API Endpoints Overview

### 1. Create a Chatbot

**POST** `/chatbots/create-chatbot`

Create a new chatbot instance to which you can upload data and query.

**Request Body:**

```json
{
  "name": "My First Chatbot",
  "description": "Customer support bot for product X"
}
```

**Response:**

```json
{
  "chatbot_id": 1,
  "name": "My First Chatbot",
  "description": "Customer support bot for product X"
}
```

---

### 2. List Your Chatbots

**GET** `/chatbots/my-chatbots`

Returns all chatbots you have created.

**Response:**

```json
[
  {
    "chatbot_id": 1,
    "name": "My First Chatbot",
    "description": "Customer support bot for product X"
  },
  {
    "chatbot_id": 2,
    "name": "Sales Bot",
    "description": "Handles sales questions"
  }
]
```

---

### 3. Upload Text Data

**POST** `/process/text`

Upload plain text data to train your chatbot's vector store.

**Request Body:**

```json
{
  "text": "Your custom knowledge or document text goes here...",
  "file_name": "custom_text_data",
  "chatbot_id": 1
}
```

---

### 4. Upload Files (PDF, Docs, etc.)

**POST** `/process/upload-file/`

Upload document files for extraction and training.

- Use multipart/form-data
- Field: `file_input` for the file
- JSON fields inside form-data:

```json
{
  "file_name": "uploaded_doc_name",
  "chatbot_id": 1
}
```

Example using `curl`:

```bash
curl -X POST http://localhost:3000/process/upload-file/ \
  -H "x-api-key: YOUR_API_KEY" \
  -F "file_input=@/path/to/your/file.pdf" \
  -F "file_name=uploaded_doc_name" \
  -F "chatbot_id=1"
```

---

### 5. Upload Q&A Pairs

**POST** `/process/qa`

Upload structured Q&A pairs for training your chatbot.

**Request Body:**

```json
{
  "qa_list": [
    {
      "question": "What is your return policy?",
      "answer": "You can return any item within 30 days of purchase."
    },
    {
      "question": "How to contact support?",
      "answer": "Email us at support@example.com."
    }
  ],
  "file_name": "faq_data",
  "chatbot_id": 1
}
```

---

### 6. Get Data Sources for a Chatbot

**GET** `/process/my-data-sources/{chatbot_id}`

Retrieve all data sources (texts, files, Q&A) uploaded and indexed for a specific chatbot.

Example:

```bash
GET http://localhost:3000/process/my-data-sources/1
```

**Response:**

```json
[
  {
    "file_name": "custom_text_data",
    "type": "text",
    "uploaded_at": "2025-05-20T12:34:56Z"
  },
  {
    "file_name": "uploaded_doc_name",
    "type": "file",
    "uploaded_at": "2025-05-19T10:00:00Z"
  },
  {
    "file_name": "faq_data",
    "type": "qa",
    "uploaded_at": "2025-05-18T15:20:30Z"
  }
]
```

---

### 7. Query the Chatbot

**POST** `/chatbots/chat`

Send a query to your chatbot and get an AI-generated response.

**Request Body:**

```json
{
  "text": "How can I return a product?",
  "model_name": "llama3",  // or "mistral7b"
  "chatbot_id": 1
}
```

**Response:**

```json
{
  "response": "You can return any item within 30 days of purchase. Make sure to keep the receipt."
}
```

---

## Typical Workflow Example

1. **Create a chatbot**

```bash
POST /chatbots/create-chatbot
{
  "name": "Support Bot",
  "description": "Handles customer queries"
}
```

2. **Upload documents or text**

```bash
POST /process/upload-file/ (with your PDF or DOC)
OR
POST /process/text (for plain text)
```

3. **Add Q&A pairs if available**

```bash
POST /process/qa
```

4. **Query your chatbot**

```bash
POST /chatbots/chat
{
  "text": "How do I reset my password?",
  "model_name": "llama3",
  "chatbot_id": 1
}
```

---

## Dev Environment & Testing

### Makefile Commands
| Command              | Description |
|----------------------|-------------|
| `make build`         | Build all containers using Docker Compose |
| `make up`            | Start all services in the background |
| `make down`          | Stop and remove all containers |
| `make clean`         | Stop and remove containers and images |
| `make start`         | Build and then start all containers |
| `make rebuild`       | Clean, build and start containers from scratch |
| `make logs`          | Tail logs from the `promptly` service |
| `make logs-db`       | Tail logs from the `db` service |
| `make shell-backend` | Open a bash shell into the `promptly` backend container |
| `make test`          | Run tests using Pytest inside the container |
| `make wait-for-db`   | Wait for the DB service to be ready |
| `make alembic-upgrade`   | Run Alembic migrations to latest head |
| `make alembic-downgrade` | Roll back the last Alembic migration |
| `make alembic-revision`  | Autogenerate a new Alembic migration |
| `make alembic-migrate`   | Generate and apply a new Alembic migration |

---

### .env Configuration (Example)
```
POSTGRES_USER=user_xyz789
POSTGRES_PASSWORD=SecurePass#9876
POSTGRES_DB=my_test_db
POSTGRES_PORT=5433
POSTGRES_HOST=localhost
POSTGRES_URL=postgresql://user_xyz789:SecurePass#9876@localhost:5433/my_test_db
JWT_SECRET_KEY=SECRET_KEY
JWT_ALGORITHM=HS256
JWT_ACESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_PORT=3000
API_KEY=API_KEY_xyz789
```

---

## GitHub Actions CI

Promptly CI is configured to run on pushes and pull requests to the `main` branch. It runs full Docker-based test suites.

### Secret Environment Variables Used
| Variable | Description |
|----------|-------------|
| `POSTGRES_USER` | Database username |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_URL` | Full database connection string |
| `POSTGRES_DB` | Name of the test database used in CI |
| `POSTGRES_PORT` | Port on which the database service listens |
| `POSTGRES_HOST` | Database host (e.g., `db` in docker-compose context) |
| `JWT_SECRET` | Secret key for signing JWT tokens |
| `API_KEY` | API key used for authentication with Promptly API |
| `BACKEND_PORT` | Backend port to run services in CI (e.g., 8230) |

### CI Pipeline Steps
1. Check out the repository
2. Create a `.env` file with injected secrets
3. Set up Docker Buildx
4. Build and start containers using `make start`
5. Wait for the database to be ready
6. Run Alembic migrations
7. Run tests using `make test`
8. Tear down services using `make down`

---

## Notes
- Models must exist locally in `llms/gguf/models/`
- Chatbots are isolated; each chatbot’s vectorstore is independent
- Uploaded data can be files, QA pairs, or plain text

---

For support, contact your Promptly administrator or refer to internal documentation.


## Troubleshooting & Tips

- Make sure your `chatbot_id` is correct and belongs to you.
- Use the correct `model_name` from the supported list: currently `llama3` or `mistral7b`.
- Large files might take some time to process and index.
- Check logs using `make logs` if running locally with Docker.
- Keep your `API_KEY` secure and do not expose it publicly.

---

## Next Steps

- You can integrate these APIs in your app, website, or internal tools.
- Use the API key for authentication.
- Build multiple chatbots for different projects or clients.
- Monitor data sources and retrain your bots by uploading new data anytime.

---

If you have questions or want to contribute, please visit the main repo: [Promptly GitHub](https://github.com/SaidiSouhaieb/promptly-ai-backend)

---

# Thank you for using Promptly! 🚀
