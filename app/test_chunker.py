from text_chunker import split_text_into_chunks

sample_text = """
Deep learning uses neural networks.
CNNs are used for image processing.
Pooling reduces feature map dimensions.
RNNs are used for sequential data.
"""

chunks = split_text_into_chunks(
    sample_text,
    chunk_size=50,
    overlap=10
)

for i, chunk in enumerate(chunks, start=1):

    print(f"\nChunk {i}:")
    print(chunk)