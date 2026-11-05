from pdf_reader import extract_text_from_pdf

pdf_path = "data/documents/deep_learning_notes.pdf"

text = extract_text_from_pdf(pdf_path)

print("PDF extraction successful!")
print("\nExtracted text:")
print(text[:2000])