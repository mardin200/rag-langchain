import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

CHAT_MODEL = os.getenv(
    "CHAT_MODEL",
    "gpt-5-nano",
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
)


DATA_DIR = BASE_DIR / "data"

DOCUMENTS_DIR = DATA_DIR / "documents"
EVALUATION_DIR = DATA_DIR / "evaluation"

CHROMA_DIR = BASE_DIR / "chroma"

UPLOADS_DIR = BASE_DIR / "uploads"


DOCUMENTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

EVALUATION_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

CHROMA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

UPLOADS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)