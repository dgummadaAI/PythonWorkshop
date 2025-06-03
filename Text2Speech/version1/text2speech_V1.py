import os
import sys
import pyttsx3
import PyPDF2

def speak_text(text, rate=150):
    engine = pyttsx3.init()

    # Select a child-like or female voice (if available)
    voices = engine.getProperty('voices')
    selected_voice = None
    for v in voices:
        if "child" in v.name.lower() or "kid" in v.name.lower() or "female" in v.name.lower():
            selected_voice = v.id
            break
    if selected_voice:
        engine.setProperty('voice', selected_voice)
    elif voices:
        engine.setProperty('voice', voices[0].id)

    engine.setProperty('rate', rate)  # Slower for better clarity
    engine.say(text)
    engine.runAndWait()

def read_text_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def read_pdf_file(path, page_number=None):
    with open(path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)

        if page_number is not None:
            if page_number < 1 or page_number > num_pages:
                raise ValueError(f"Invalid page number. The PDF has {num_pages} pages.")
            text = reader.pages[page_number - 1].extract_text()
            return f"Reading page {page_number}:\n{text}"
        else:
            full_text = ""
            for i, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                full_text += f"\n--- Page {i} ---\n{page_text}\n"
            return full_text

def process_file(file_path, page_number=None):
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        return

    ext = os.path.splitext(file_path)[1].lower()
    print(f"Processing file: {file_path}")

    try:
        if ext == '.txt':
            content = read_text_file(file_path)
        elif ext == '.pdf':
            content = read_pdf_file(file_path, page_number)
        else:
            print("Unsupported file type. Please provide a .txt or .pdf file.")
            return

        print("Starting text-to-speech...")
        speak_text(content)

    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python text_to_speech_reader.py <file_path> [page_number]")
        sys.exit(1)

    file_path = sys.argv[1]
    page_number = None

    if len(sys.argv) >= 3:
        try:
            page_number = int(sys.argv[2])
        except ValueError:
            print("Invalid page number. It must be an integer.")
            sys.exit(1)

    process_file(file_path, page_number)
