from sentence_transformers import SentenceTransformer


# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(text_list):

    # Convert text into numerical vectors
    embeddings = model.encode(text_list)

    return embeddings


if __name__ == "__main__":

    sentences = [
        "CNN is used for image classification.",
        "Convolutional neural networks identify objects in pictures.",
        "RNN is used for sequential data."
    ]

    embeddings = generate_embeddings(sentences)

    print("Embedding generation successful!")

    print("\nNumber of sentences:", len(sentences))

    print("Embedding shape:", embeddings.shape)

    print("\nFirst sentence embedding:")
    print(embeddings[0])