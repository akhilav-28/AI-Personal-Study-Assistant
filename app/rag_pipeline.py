
from retriever import search_documents
from llm_generator import generate_answer


def ask_question(question, document_name=None):

    results = search_documents(
        question,
        top_k=5,
        document_name=document_name,
        distance_threshold=0.8
    )

    if not results:
        return (
            "I couldn't find sufficiently relevant information "
            "in your study material.",
            []
        )

    # Use only the two closest matches
    results = results[:2]

    context = "\n\n".join(
        result["text"]
        for result in results
    )

    answer = generate_answer(
        question,
        context
    )

    sources = []

    for result in results:

        metadata = result["metadata"]

        sources.append({
            "text": result["text"],
            "page_number": metadata.get("page_number"),
            "document_name": metadata.get("document_name"),
            "distance": result["distance"]
        })

    return answer, sources
