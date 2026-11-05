
from sentence_transformers import SentenceTransformer
import chromadb


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Connect to ChromaDB
client = chromadb.PersistentClient(
    path="data/chroma_db"
)

collection = client.get_collection(
    name="study_materials"
)


def search_documents(
    question,
    top_k=3,
    document_name=None,
    distance_threshold=1.0
):

    # Convert question into an embedding
    question_embedding = model.encode([question])

    query_options = {
        "query_embeddings": question_embedding.tolist(),
        "n_results": top_k,
        "include": [
            "documents",
            "metadatas",
            "distances"
        ]
    }

    # Search only the selected document when provided
    if document_name:
        query_options["where"] = {
            "document_name": document_name
        }

    results = collection.query(**query_options)

    if not results or not results["documents"][0]:
        return []

    relevant_results = []

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):

        # Keep only passages within the threshold
        if distance <= distance_threshold:

            relevant_results.append({
                "text": document,
                "metadata": metadata,
                "distance": distance
            })

    return relevant_results


if __name__ == "__main__":

    question = "What is the purpose of pooling in CNN?"

    results = search_documents(question)

    print("Question:", question)
    print("\nRelevant passages:")

    if results:

        for i, result in enumerate(results, start=1):

            print(f"\nResult {i}:")
            print(result["text"])
            print("Page:", result["metadata"].get("page_number"))
            print("Distance:", result["distance"])

    else:
        print("No sufficiently relevant passages found.")
