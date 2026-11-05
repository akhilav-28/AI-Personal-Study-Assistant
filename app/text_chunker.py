import re


SUBHEADINGS = {
    "important terms",
    "common terms",
    "convolution layer",
    "activation function",
    "pooling layer",
    "fully connected layer",
}


def is_heading(line):
    line = line.strip()

    numbered_heading = bool(
        re.match(r"^\d+\.\s+", line)
    )

    known_subheading = line.lower() in SUBHEADINGS

    return numbered_heading or known_subheading


def split_text_into_chunks(pages, chunk_size=500, overlap=50):

    all_chunks = []

    for page in pages:

        page_number = page["page_number"]
        lines = page["text"].splitlines()

        sections = []
        current_section = []

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if is_heading(line) and current_section:
                sections.append(current_section)
                current_section = []

            current_section.append(line)

        if current_section:
            sections.append(current_section)

        for section in sections:

            section_text = " ".join(section)

            sentences = re.split(
                r"(?<=[.!?])\s+",
                section_text
            )

            current_sentences = []
            current_length = 0

            for sentence in sentences:

                sentence = sentence.strip()

                if not sentence:
                    continue

                sentence_length = len(sentence)

                if (
                    current_sentences
                    and current_length + sentence_length > chunk_size
                ):

                    all_chunks.append({
                        "text": " ".join(current_sentences),
                        "page_number": page_number
                    })

                    # Preserve complete sentences for overlap
                    overlap_sentences = []
                    overlap_length = 0

                    for old_sentence in reversed(current_sentences):

                        if overlap_length + len(old_sentence) > overlap:
                            break

                        overlap_sentences.insert(0, old_sentence)
                        overlap_length += len(old_sentence)

                    current_sentences = overlap_sentences
                    current_length = overlap_length

                current_sentences.append(sentence)
                current_length += sentence_length

            if current_sentences:

                all_chunks.append({
                    "text": " ".join(current_sentences),
                    "page_number": page_number
                })

    return all_chunks