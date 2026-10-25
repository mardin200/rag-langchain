from pathlib import Path

from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}


def load_document(file_path: Path):

    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        loader = PyPDFLoader(
            str(file_path)
        )

    elif suffix == ".docx":
        loader = Docx2txtLoader(
            str(file_path)
        )

    elif suffix == ".txt":
        loader = TextLoader(
            str(file_path),
            encoding="utf-8",
        )

    elif suffix == ".md":
        loader = UnstructuredMarkdownLoader(
            str(file_path)
        )

    else:
        raise ValueError(
            f"Unsupported file type: {suffix}"
        )

    return loader.load()