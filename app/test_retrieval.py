from app.vector_store import get_retriever

query = "سوابق محمد الیاسی در زمینه امنیت نرم افزار چیست؟"

retriever = get_retriever(k=4)

documents = retriever.invoke(query)

print("\n===== RETRIEVAL RESULT =====\n")

for i, doc in enumerate(documents, start=1):
    print(f"--- Document {i} ---")
    print("Content:")
    print(doc.page_content)

    print("\nMetadata:")
    print(doc.metadata)

    print("\n" + "=" * 60 + "\n")