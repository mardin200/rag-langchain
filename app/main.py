from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import UPLOADS_DIR
from app.document_loader import (
    SUPPORTED_EXTENSIONS,
    load_document,
)
from app.rag_service import (
    answer_question,
    index_documents,
    search_with_scores,
)
from app.vector_store import (
    delete_document,
)

BASE_DIR = Path(
    __file__
).resolve().parent.parent


TEMPLATES_DIR = (
    BASE_DIR / "templates"
)

STATIC_DIR = (
    BASE_DIR / "static"
)


app = FastAPI(
    title="RAG LangChain",
    description=(
        "A learning project "
        "for building a RAG system "
        "with LangChain"
    ),
    version="0.5.1",
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(
            STATIC_DIR
        )
    ),
    name="static",
)


templates = Jinja2Templates(
    directory=str(
        TEMPLATES_DIR
    )
)


@app.get(
    "/",
    response_class=HTMLResponse,
)
async def home(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get(
    "/api/health"
)
async def health_check():

    return {
        "status": "ok",
        "application": "rag-langchain",
        "version": "0.5.1",
    }


@app.get(
    "/api/documents"
)
async def list_documents():

    documents = []

    for file_path in UPLOADS_DIR.iterdir():

        if not file_path.is_file():
            continue

        suffix = (
            file_path.suffix.lower()
        )

        if suffix not in (
            SUPPORTED_EXTENSIONS
        ):
            continue

        document_id = (
            file_path.stem
        )

        documents.append(
            {
                "document_id": document_id,
                "filename": file_path.name,
                "file_type": suffix,
                "file_size": (
                    file_path.stat().st_size
                ),
            }
        )

    return {
        "documents": documents
    }


@app.post(
    "/api/documents/upload"
)
async def upload_document(
    file: UploadFile = File(...) # noqa: B008
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )


    original_filename = Path(
        file.filename
    ).name


    suffix = Path(
        original_filename
    ).suffix.lower()


    if suffix not in SUPPORTED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Supported types: "
                "PDF, DOCX, TXT, MD."
            ),
        )


    document_id = str(
        uuid4()
    )


    safe_filename = (
        f"{document_id}{suffix}"
    )


    file_path = (
        UPLOADS_DIR
        / safe_filename
    )


    content = await file.read()

    file_path.write_bytes(
        content
    )


    try:

        documents = load_document(
            file_path
        )

        chunks = index_documents(
            documents,
            document_id,
            original_filename,
        )

    except Exception as exc: # noqa: BLE001

        file_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=400,
            detail=(
                f"Could not process "
                f"document: {exc}"
            ),
        )


    full_text = "\n\n".join(
        document.page_content
        for document in documents
    )


    return {
        "document_id": document_id,
        "filename": original_filename,
        "file_type": suffix,
        "file_size": len(content),
        "uploaded_at": (
            datetime.now(
                UTC
            ).isoformat()
        ),
        "documents": len(
            documents
        ),
        "chunks": len(
            chunks
        ),
        "text_length": len(
            full_text
        ),
    }


@app.delete(
    "/api/documents/{document_id}"
)
async def delete_document_api(
    document_id: str,
):

    matching_files = list(
        UPLOADS_DIR.glob(
            f"{document_id}.*"
        )
    )


    if not matching_files:

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )


    try:

        delete_document(
            document_id
        )

        for file_path in matching_files:

            file_path.unlink(
                missing_ok=True
            )

    except Exception as exc: # noqa: BLE001

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not delete "
                f"document: {exc}"
            ),
        )


    return {
        "document_id": document_id,
        "status": "deleted",
    }


@app.get(
    "/api/search"
)
async def search(
    q: str,
    k: int = 4,
):

    if not q.strip():

        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )


    results = search_with_scores(
        query=q,
        k=k,
    )


    return {
        "query": q,
        "k": k,
        "results": results,
    }


@app.post(
    "/api/chat"
)
async def chat(
    request: Request,
):

    body = await request.json()


    query = body.get(
        "query",
        "",
    ).strip()


    history = body.get(
        "history",
        [],
    )


    if not query:

        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )


    try:

        result = answer_question(
            query=query,
            history=history,
        )

    except Exception as exc: # noqa: BLE001

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not generate answer: "
                f"{exc}"
            ),
        )


    return {
        "query": query,
        "answer": result["answer"],
        "sources": result["sources"],
    }