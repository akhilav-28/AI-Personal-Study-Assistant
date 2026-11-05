
import os
import re
import tempfile
import streamlit as st

from pdf_reader import extract_pages_from_pdf
from text_chunker import split_text_into_chunks
from embedding_generator import generate_embeddings
from vector_store import store_document, collection
from rag_pipeline import ask_question
from summarizer import summarize_document
from question_generator import generate_revision_questions


# ==================================================
# APP CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AI Personal Study Assistant",
    page_icon="📚",
    layout="wide"
)

DOCUMENT_FOLDER = "data/documents"

os.makedirs(DOCUMENT_FOLDER, exist_ok=True)

st.title("📚 AI Personal Study Assistant")
st.write(
    "Upload multiple PDFs, ask questions, generate summaries "
    "and prepare for examinations using AI."
)


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def get_indexed_documents():

    try:
        results = collection.get(
            include=["metadatas"]
        )

        documents = set()

        for metadata in results.get("metadatas", []):

            if metadata and metadata.get("document_name"):
                documents.add(metadata["document_name"])

        return sorted(documents)

    except Exception as error:

        st.error(f"Unable to retrieve documents: {error}")
        return []


def parse_mcqs(text):

    questions = []

    pattern = re.compile(
        r"\*\*(\d+)\.\s*(.*?)\*\*\s*"
        r"A\)\s*(.*?)\s*"
        r"B\)\s*(.*?)\s*"
        r"C\)\s*(.*?)\s*"
        r"D\)\s*(.*?)\s*"
        r"\*\*Correct Answer:\s*([A-D])\*\*\s*"
        r"\*Explanation:\s*(.*?)\*",
        re.DOTALL
    )

    for match in pattern.finditer(text):

        questions.append({
            "question": match.group(2).strip(),
            "options": [
                match.group(3).strip(),
                match.group(4).strip(),
                match.group(5).strip(),
                match.group(6).strip()
            ],
            "correct_answer": match.group(7).strip(),
            "explanation": match.group(8).strip()
        })

    return questions


def load_document_pages(document_name):

    pdf_path = os.path.join(
        DOCUMENT_FOLDER,
        document_name
    )

    if not os.path.isfile(pdf_path):
        return None

    return extract_pages_from_pdf(pdf_path)


# ==================================================
# 1. MULTIPLE PDF UPLOAD
# ==================================================

st.header("📄 Document Management")

uploaded_files = st.file_uploader(
    "Upload one or more PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    if st.button("Process Uploaded PDFs", type="primary"):

        successful = 0

        for uploaded_file in uploaded_files:

            st.write(f"Processing: {uploaded_file.name}")

            safe_name = os.path.basename(uploaded_file.name)

            pdf_path = os.path.join(
                DOCUMENT_FOLDER,
                safe_name
            )

            try:

                with open(pdf_path, "wb") as file:
                    file.write(uploaded_file.getbuffer())

                with st.spinner(f"Processing {safe_name}..."):

                    pages = extract_pages_from_pdf(pdf_path)

                    chunks = split_text_into_chunks(
                        pages,
                        chunk_size=500,
                        overlap=50
                    )

                    if not chunks:
                        st.warning(
                            f"No readable text found in {safe_name}."
                        )
                        continue

                    chunk_texts = [
                        chunk["text"]
                        for chunk in chunks
                    ]

                    embeddings = generate_embeddings(chunk_texts)

                    store_document(
                        chunks,
                        embeddings,
                        safe_name
                    )

                    successful += 1

                st.success(
                    f"{safe_name} processed successfully!"
                )

            except Exception as error:

                st.error(
                    f"Error processing {safe_name}: {error}"
                )

        if successful:
            st.success(
                f"Successfully processed {successful} PDF file(s)."
            )
            st.rerun()


# ==================================================
# 2. DOCUMENT SELECTION
# ==================================================

documents = get_indexed_documents()

st.subheader("📚 Your Study Documents")

if documents:

    selected_document = st.selectbox(
        "Select a document to study",
        documents
    )

    st.info(f"Selected document: {selected_document}")

else:

    selected_document = None

    st.warning(
        "No indexed documents found. Upload and process a PDF first."
    )


# ==================================================
# 3. DELETE DOCUMENT
# ==================================================

if documents:

    with st.expander("🗑️ Delete a Document"):

        delete_document = st.selectbox(
            "Choose document to delete",
            documents,
            key="delete_document"
        )

        confirm_delete = st.checkbox(
            "I confirm that I want to delete this document."
        )

        if st.button("Delete Selected Document"):

            if not confirm_delete:

                st.warning("Please confirm before deleting.")

            else:

                try:

                    collection.delete(
                        where={
                            "document_name": delete_document
                        }
                    )

                    pdf_path = os.path.join(
                        DOCUMENT_FOLDER,
                        delete_document
                    )

                    if os.path.isfile(pdf_path):
                        os.remove(pdf_path)

                    for key in list(st.session_state.keys()):

                        if delete_document in key:
                            del st.session_state[key]

                    st.success(
                        f"{delete_document} deleted successfully."
                    )

                    st.rerun()

                except Exception as error:

                    st.error(f"Deletion failed: {error}")


# ==================================================
# LOAD SELECTED DOCUMENT
# ==================================================

pages = None

if selected_document:

    try:
        pages = load_document_pages(selected_document)

        if pages is None:

            st.warning(
                "The PDF file is missing from data/documents. "
                "Upload and process it again to use summarization "
                "and revision-question generation."
            )

    except Exception as error:

        st.error(f"Unable to read the selected PDF: {error}")


# ==================================================
# 4. PDF SUMMARIZATION
# ==================================================

st.header("📖 PDF Summarization")

if selected_document and pages:

    summary_key = f"summary_{selected_document}"

    if st.button("Generate Summary"):

        with st.spinner("Generating summary..."):

            try:

                summary = summarize_document(pages)

                st.session_state[summary_key] = summary

            except Exception as error:

                st.error(f"Summary generation failed: {error}")

    if summary_key in st.session_state:

        st.subheader("Document Summary")
        st.markdown(st.session_state[summary_key])


# ==================================================
# 5. REVISION QUESTION GENERATOR
# ==================================================

st.header("📝 Revision Question Generator")

if selected_document and pages:

    revision_key = f"revision_{selected_document}"
    quiz_key = f"quiz_{selected_document}"

    if st.button("Generate Revision Questions"):

        with st.spinner("Generating revision questions..."):

            try:

                revision_text = generate_revision_questions(pages)

                st.session_state[revision_key] = revision_text

                mcqs = parse_mcqs(revision_text)

                st.session_state[quiz_key] = mcqs
                st.session_state[f"quiz_answers_{selected_document}"] = {}
                st.session_state[f"quiz_submitted_{selected_document}"] = False

            except Exception as error:

                st.error(
                    f"Question generation failed: {error}"
                )

    if revision_key in st.session_state:

        st.subheader("Generated Revision Questions")

        st.markdown(
            st.session_state[revision_key]
        )


# ==================================================
# 6. INTERACTIVE MCQ QUIZ
# ==================================================

st.header("🎯 Interactive MCQ Quiz")

if selected_document:

    quiz_key = f"quiz_{selected_document}"
    answers_key = f"quiz_answers_{selected_document}"
    submitted_key = f"quiz_submitted_{selected_document}"

    quiz_questions = st.session_state.get(
        quiz_key,
        []
    )

    if quiz_questions:

        answers = st.session_state.get(
            answers_key,
            {}
        )

        st.write(
            f"Total questions: {len(quiz_questions)}"
        )

        if not st.session_state.get(submitted_key, False):

            for i, item in enumerate(quiz_questions):

                st.markdown(
                    f"**Question {i + 1}: {item['question']}**"
                )

                selected_answer = st.radio(
                    "Choose your answer:",
                    options=["A", "B", "C", "D"],
                    format_func=lambda option, q=item: (
                        f"{option}) "
                        f"{q['options'][ord(option) - ord('A')]}"
                    ),
                    key=f"{selected_document}_mcq_{i}",
                    index=None
                )

                if selected_answer:
                    answers[i] = selected_answer

                st.divider()

            st.session_state[answers_key] = answers

            if st.button("Submit Quiz"):

                st.session_state[submitted_key] = True
                st.rerun()

        else:

            score = 0

            st.subheader("📊 Quiz Results")

            for i, item in enumerate(quiz_questions):

                selected_answer = answers.get(i)
                correct_answer = item["correct_answer"]

                if selected_answer == correct_answer:

                    score += 1

                    st.success(
                        f"Question {i + 1}: Correct!"
                    )

                else:

                    st.error(
                        f"Question {i + 1}: Incorrect. "
                        f"Correct answer: {correct_answer}"
                    )

                st.write(item["explanation"])

            total = len(quiz_questions)

            st.markdown(
                f"### Your Score: {score}/{total}"
            )

            st.progress(score / total)

            if score == total:

                st.success("Excellent! Perfect score!")

            elif score >= total / 2:

                st.info("Good work! Review your incorrect answers.")

            else:

                st.warning(
                    "Keep practising. Review your study material."
                )

            if st.button("Restart Quiz"):

                st.session_state[answers_key] = {}
                st.session_state[submitted_key] = False

                for i in range(total):

                    st.session_state.pop(
                        f"{selected_document}_mcq_{i}",
                        None
                    )

                st.rerun()

    else:

        st.info(
            "Generate revision questions first to start the quiz."
        )


# ==================================================
# 7. DOCUMENT-SPECIFIC QUESTION ANSWERING
# ==================================================

st.header("💬 Ask Questions")

if selected_document:

    question = st.text_input(
        "Ask something about the selected PDF:",
        key=f"question_input_{selected_document}"
    )

    if st.button("Get Answer"):

        if not question.strip():

            st.warning("Please enter a question.")

        else:

            with st.spinner("Searching and generating an answer..."):

                try:

                    answer, sources = ask_question(
                        question,
                        document_name=selected_document
                    )

                    history_key = f"chat_history_{selected_document}"

                    if history_key not in st.session_state:
                        st.session_state[history_key] = []

                    st.session_state[history_key].append({
                        "question": question,
                        "answer": answer,
                        "sources": sources
                    })

                except Exception as error:

                    st.error(
                        f"Unable to generate answer: {error}"
                    )


# ==================================================
# 8. CHAT HISTORY
# ==================================================

st.header("💭 Chat History")

if selected_document:

    history_key = f"chat_history_{selected_document}"

    history = st.session_state.get(
        history_key,
        []
    )

    if history:

        for i, chat in enumerate(history, start=1):

            with st.expander(
                f"Question {i}: {chat['question']}"
            ):

                st.markdown("**AI Answer**")

                st.write(chat["answer"])

                st.markdown("**Sources**")

                if chat["sources"]:

                    for source_number, source in enumerate(
                        chat["sources"],
                        start=1
                    ):

                        st.write(
                            f"Source {source_number}: "
                            f"{source['text']}"
                        )

                        st.caption(
                            f"Page: {source['page_number']} | "
                            f"Distance: {source['distance']:.4f}"
                        )

                else:

                    st.write("No relevant sources found.")

        if st.button("Clear Chat History"):

            st.session_state[history_key] = []
            st.rerun()

    else:

        st.info("No questions asked yet for this document.")


# ==================================================
# 9. FOOTER
# ==================================================

st.divider()

st.caption(
    "AI Personal Study Assistant | "
    "Built with Python, Streamlit, Sentence Transformers, "
    "ChromaDB and Gemini."
)
