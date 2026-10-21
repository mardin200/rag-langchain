from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.config import (
    CHROMA_DIR,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
)


COLLECTION_NAME = "rag_documents"


def get_embeddings():

    if not EMBEDDING_MODEL:
        raise ValueError(
            "EMBEDDING_MODEL is not configured in .env"
        )

    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )


def get_vector_store():

    embeddings = get_embeddings()

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )


def add_documents(documents):

    vector_store = get_vector_store()

    vector_store.add_documents(
        documents
    )

    return vector_store


def search_documents(
    query: str,
    k: int = 4,
):

    vector_store = get_vector_store()

    return vector_store.similarity_search(
        query,
        k=k,
    )


def search_documents_with_scores(
    query: str,
    k: int = 4,
):

    vector_store = get_vector_store()

    return vector_store.similarity_search_with_score(
        query,
        k=k,
    )


def get_retriever(
    k: int = 4,
):

    vector_store = get_vector_store()

    return vector_store.as_retriever(
        search_kwargs={
            "k": k
        }
    )


def delete_document(
    document_id: str,
):

    vector_store = get_vector_store()

    collection = vector_store._collection

    collection.delete(
        where={
            "document_id": document_id
        }
    )