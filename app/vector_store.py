import chromadb

client = chromadb.PersistentClient(
    path="data/chroma_db"
)

collection = client.get_or_create_collection(
    name="study_materials"
)


def store_document(chunks, embeddings, document_name):

    # Remove previous chunks from this document
    collection.delete(
        where={"document_name": document_name}
    )

    ids = [
        f"{document_name}_{i}"
        for i in range(len(chunks))
    ]

    documents = [
        chunk["text"]
        for chunk in chunks
    ]

    metadatas = [
        {
            "document_name": document_name,
            "page_number": chunk["page_number"]
        }
        for chunk in chunks
    ]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print("Document stored successfully!")


if __name__ == "__main__":

    print("Vector database initialized!")
    print("Collection name:", collection.name)