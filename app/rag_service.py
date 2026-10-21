from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from app.config import (
    CHAT_MODEL,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
)

from app.vector_store import (
    add_documents,
    get_retriever,
    search_documents_with_scores,
)


def split_documents(
    documents: list[Document],
) -> list[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        length_function=len,
    )

    return splitter.split_documents(
        documents
    )


def index_documents(
    documents: list[Document],
    document_id: str,
    filename: str,
):

    chunks = split_documents(
        documents
    )

    for chunk in chunks:

        chunk.metadata["document_id"] = (
            document_id
        )

        chunk.metadata["filename"] = (
            filename
        )

    add_documents(
        chunks
    )

    return chunks


def get_llm():

    return ChatOpenAI(
        model=CHAT_MODEL,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )


def build_context(
    documents: list[Document],
) -> str:

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        filename = document.metadata.get(
            "filename",
            "Unknown",
        )

        page = document.metadata.get(
            "page"
        )

        if page is not None:

            source = (
                f"{filename}, "
                f"page {page + 1}"
            )

        else:

            source = filename

        context_parts.append(
            f"[Source {index}: {source}]\n"
            f"{document.page_content}"
        )

    return "\n\n".join(
        context_parts
    )


def build_sources(
    documents: list[Document],
) -> list[dict]:

    sources = []

    seen = set()

    for document in documents:

        document_id = document.metadata.get(
            "document_id"
        )

        filename = document.metadata.get(
            "filename"
        )

        page = document.metadata.get(
            "page"
        )

        key = (
            document_id,
            filename,
            page,
        )

        if key in seen:
            continue

        seen.add(key)

        sources.append(
            {
                "document_id": document_id,
                "filename": filename,
                "page": (
                    page + 1
                    if page is not None
                    else None
                ),
            }
        )

    return sources


def search_with_scores(
    query: str,
    k: int = 4,
):

    results = search_documents_with_scores(
        query=query,
        k=k,
    )

    output = []

    for document, score in results:

        output.append(
            {
                "content": (
                    document.page_content
                ),
                "metadata": (
                    document.metadata
                ),
                "score": score,
            }
        )

    return output


def answer_question(
    query: str,
    history: list[dict] | None = None,
) -> dict:

    retriever = get_retriever(
        k=4
    )

    documents = retriever.invoke(
        query
    )

    context = build_context(
        documents
    )

    sources = build_sources(
        documents
    )

    history_text = ""

    if history:

        history_parts = []

        for message in history:

            role = message.get(
                "role",
                "",
            )

            content = message.get(
                "content",
                "",
            )

            if role and content:

                history_parts.append(
                    f"{role}: {content}"
                )

        history_text = "\n".join(
            history_parts
        )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a helpful assistant.

Answer the user's question ONLY
based on the provided context.

Use the conversation history only
to understand references and context
in the user's current question.

If the answer cannot be found
in the provided context, say that
the information is not available
in the provided documents.

Do not use outside knowledge.

Conversation history:
{history}

Context:
{context}
""",
            ),
            (
                "human",
                "{question}",
            ),
        ]
    )

    llm = get_llm()

    chain = (
        prompt
        | llm
    )

    response = chain.invoke(
        {
            "history": history_text,
            "context": context,
            "question": query,
        }
    )

    return {
        "answer": response.content,
        "sources": sources,
    }