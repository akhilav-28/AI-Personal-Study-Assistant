from pdf_reader import extract_pages_from_pdf
from text_chunker import split_text_into_chunks


def process_document(pdf_path):

    pages = extract_pages_from_pdf(pdf_path)

    chunks = split_text_into_chunks(
        pages,
        chunk_size=500,
        overlap=50
    )

    return chunks


if __name__ == "__main__":

    pdf_path = "data/documents/deep_learning_notes.pdf"

    chunks = process_document(pdf_path)

    print("Document processing successful!")
    print(f"\nTotal chunks created: {len(chunks)}")

    for i, chunk in enumerate(chunks, start=1):

        print(f"\n--- Chunk {i} ---")
        print("Page:", chunk["page_number"])
        print(chunk["text"])