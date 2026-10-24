# RAG LangChain

A document-based Retrieval-Augmented Generation (RAG) application built with LangChain, FastAPI, and ChromaDB.

The application allows users to upload documents, search their contents semantically, and ask questions through a chat interface. Answers are generated using relevant document content retrieved from the vector database.

## Features

- **Document Management:** Upload, list, and delete documents.
- **Automatic Indexing:** Uploaded documents are processed, split into smaller chunks, and indexed in ChromaDB.
- **Semantic Search:** Find relevant passages based on the meaning of a query.
- **Document-Based Chat:** Ask questions about your documents and receive answers grounded in retrieved content.
- **Source References:** View the source filenames and page numbers associated with chat answers when available.
- **Conversation Context:** Use previous messages to clarify follow-up questions within the current chat session.
- **Docker Support:** Run the application using Docker Compose.

## Tech Stack

- **Python 3.13** — application runtime
- **FastAPI** — backend API
- **LangChain** — document processing, retrieval, and RAG pipeline
- **ChromaDB** — vector database
- **LangChain OpenAI integration** — chat and embedding model integration
- **HTML, CSS, JavaScript** — web interface
- **Docker and Docker Compose** — containerization

## Prerequisites

- Docker Desktop with Docker Compose, or a compatible Python environment for local development
- An API key for your configured model provider
- Access to compatible chat and embedding models

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/mardin200/rag-langchain.git
cd rag-langchain
```

### 2. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a reference.

Example configuration:

```dotenv
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
CHAT_MODEL=gpt-5-nano
EMBEDDING_MODEL=your-embedding-model-here
```

Replace the placeholder values with valid credentials and model names supported by your provider.

For an OpenAI-compatible provider, set `OPENAI_BASE_URL` to the appropriate API endpoint.

### 3. Start the application with Docker Compose

Build the image and start the application:

```bash
docker compose up -d --build
```

Check the container status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f
```

Stop the application:

```bash
docker compose down
```

### 4. Open the application

Once the container is running, open:

- **Web interface:** http://localhost:8000
- **Health endpoint:** http://localhost:8000/api/health

## Using the Application

The web interface contains three functional sections: Knowledge Base, Semantic Search, and Chat.

### 1. Knowledge Base — Manage Documents

The Knowledge Base section is used to upload and manage the documents available to the RAG system.

**Supported file formats:**

- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- Plain text (`.txt`)
- Markdown (`.md`)

**Upload and index a document:**

1. Open the application at http://localhost:8000.
2. Locate the **Knowledge Base** section.
3. Select a supported file using the file picker.
4. Click **Upload Document**.
5. Wait for the upload and indexing process to finish.

After a successful upload, the interface reports how many chunks were created and refreshes the document list.

During indexing, the application extracts document content, splits it into smaller text chunks, adds document metadata, and stores the chunks in ChromaDB for retrieval.

The current text splitter uses a chunk size of 800 characters and an overlap of 120 characters. This overlap helps preserve context between adjacent chunks.

**View uploaded documents:**

The document list displays the filename, file type, and file size of each supported uploaded document.

**Delete a document:**

1. Find the document in the Knowledge Base list.
2. Click its **Delete** button.
3. Confirm the deletion.

The application removes the uploaded file and its associated entries from the vector database.

> Only upload documents you are authorized to process. Uploaded content may be sent to your configured model provider as part of embedding or chat requests.

### 2. Semantic Search — Find Relevant Passages

Semantic Search retrieves document passages related to a query without requiring an exact keyword match.

**How to use it:**

1. Upload and index at least one document.
2. Locate the **Semantic Search** section.
3. Enter a question, phrase, or topic related to your documents.
4. Click **Search**.
5. Review the returned passages.

Each result can include:

- **Source:** the original filename and, when available, the page number
- **Score:** the retrieval score returned by the vector search implementation
- **Content:** the retrieved text passage

The interface currently requests up to four results per search.

Semantic Search is useful for inspecting which passages the retriever considers relevant before asking the chat model to generate an answer.

### 3. Chat — Ask Questions About Your Documents

The Chat section provides a conversational interface for asking questions about indexed documents.

**How to use it:**

1. Upload and index the documents you want to use.
2. Locate the **Chat** section.
3. Enter a question in the input field.
4. Click **Send**.
5. Read the generated answer and inspect the displayed source references, when available.

For each question, the application retrieves up to four relevant document chunks and passes their content to the configured chat model.

The system prompt instructs the model to answer using the supplied document context rather than outside knowledge. If the answer cannot be found in the retrieved context, the model is instructed to say that the information is unavailable in the provided documents.

The chat interface also sends the current conversation history with subsequent questions. This helps the model interpret follow-up questions that refer to earlier messages.

**Example workflow:**

1. Upload a PDF containing a technical specification.
2. Ask: `What are the main security requirements described in this document?`
3. Review the answer and its source references.
4. Ask a follow-up question such as: `Can you explain the second requirement in more detail?`

The quality of the answer depends on document content, retrieval quality, and the configured models. Retrieved passages and source references should be reviewed when accuracy is important.

### 4. Evaluation

The Evaluation section is currently a placeholder. Evaluation features have not yet been implemented in the web interface.

## How the RAG Pipeline Works

The application's main processing flow is:

1. **Document ingestion:** The user uploads a supported document.
2. **Text extraction:** A format-specific document loader extracts the content.
3. **Chunking:** The text is split into smaller overlapping chunks.
4. **Embedding and indexing:** The chunks are embedded and stored in ChromaDB.
5. **Retrieval:** A user query is used to retrieve relevant chunks from the vector database.
6. **Context construction:** The retrieved passages and available source metadata are assembled into context.
7. **Answer generation:** The chat model generates a response based on the retrieved context and conversation history.
8. **Source presentation:** The interface displays the answer and available source references.

## API Endpoints

The application exposes the following endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the web interface |
| `GET` | `/api/health` | Returns application health information |
| `GET` | `/api/documents` | Lists uploaded documents |
| `POST` | `/api/documents/upload` | Uploads and indexes a document |
| `DELETE` | `/api/documents/{document_id}` | Deletes a document and its indexed entries |
| `GET` | `/api/search?q=...&k=4` | Searches for relevant document passages |
| `POST` | `/api/chat` | Generates a document-grounded answer |

For interactive API exploration, open:

http://localhost:8000/docs

### Example: Chat API

Send a POST request to `/api/chat` with a JSON body:

```json
{
  "query": "What are the main topics covered in the documents?",
  "history": []
}
```

The response includes the submitted query, generated answer, and available source references.

## Configuration

The application reads its configuration from environment variables:

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | API credential for the configured provider |
| `OPENAI_BASE_URL` | API base URL |
| `CHAT_MODEL` | Chat model identifier |
| `EMBEDDING_MODEL` | Embedding model identifier |

The configured embedding model must be supported by the embedding integration used by the application.

## Data Persistence

Docker Compose mounts the local `uploads` and `chroma` directories into the container.

These bind mounts allow uploaded files and vector database data to persist when the container is recreated, provided the host directories remain intact.

Stopping or removing the container does not normally remove these host directories. Deleting the directories themselves can permanently remove application data.

## Project Structure

```text
rag-langchain/
├── app/
│   ├── config.py
│   ├── document_loader.py
│   ├── main.py
│   ├── models.py
│   ├── rag_service.py
│   ├── test_retrieval.py
│   └── vector_store.py
├── static/
│   └── style.css
├── templates/
│   └── index.html
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── .env.example
├── .gitignore
└── .dockerignore
```

Runtime data directories such as `uploads`, `chroma`, and the directories under `data` may be created automatically and are not necessarily included in a fresh clone.

## Development

To run the application locally, create and activate a Python virtual environment, install the dependencies, configure `.env`, and start Uvicorn:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The application will be available at http://localhost:8000.

## License

No license has been specified in this repository yet. Until a license is added, reuse and redistribution are subject to applicable copyright restrictions.
