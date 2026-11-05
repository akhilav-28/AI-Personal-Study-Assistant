from process_document import process_document
from embedding_generator import generate_embeddings
from vector_store import store_embeddings


# Step 1: Process the PDF
pdf_path = "data/documents/deep_learning_notes.pdf"

chunks = process_document(pdf_path)


# Step 2: Generate embeddings
embeddings = generate_embeddings(chunks)


# Step 3: Store chunks and embeddings in ChromaDB
store_embeddings(chunks, embeddings)


# Step 4: Display results
print("\nTotal chunks:", len(chunks))
print("Embedding shape:", embeddings.shape)