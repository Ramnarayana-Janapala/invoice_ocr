import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"


# ============= STREAMING VERSION =============
def query_mistral_stream(ocr_data, question):
    """Stream response from Mistral (for longer answers)"""
    prompt = f"""DOCUMENT:
{ocr_data}

QUESTION: {question}

ANSWER:"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True
    }

    response = requests.post(OLLAMA_URL, json=payload, stream=True)

    full_response = ""
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            text = chunk.get('response', '')
            print(text, end='', flush=True)
            full_response += text
    print()
    return full_response


# ============= STRUCTURED JSON OUTPUT =============
def query_mistral_json(ocr_data, extraction_task):
    """Get structured JSON output from Mistral"""
    prompt = f"""Extract information from this document text and return ONLY valid JSON.

DOCUMENT:
{ocr_data}

TASK: {extraction_task}

Return JSON:"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    response = requests.post(OLLAMA_URL, json=payload)
    try:
        return json.loads(response.json()['response'])
    except:
        return response.json()['response']


# ============= BATCH MULTIPLE DOCUMENTS =============
def batch_process_ocr(ocr_files, questions):
    """Process multiple OCR files with same questions"""
    results = {}

    for file_path in ocr_files:
        print(f"\n📄 Processing: {file_path}")
        ocr_text = open(file_path, 'r', encoding='utf-8').read()
        results[file_path] = {}

        for q in questions:
            print(f"  → {q}")
            answer = query_mistral_stream(ocr_text, q)
            results[file_path][q] = answer

    return results


# ============= USAGE =============
if __name__ == "__main__":
    # Load sample OCR
    ocr = open("ocr_output.txt").read()

    # Option 1: Stream responses
    print("=== STREAMING ===")
    query_mistral_stream(ocr, "What are the main entities in this document?")

    # Option 2: Structured extraction
    print("\n=== JSON EXTRACTION ===")
    result = query_mistral_json(ocr, "Extract: names, dates, amounts in JSON format")
    print(json.dumps(result, indent=2))

    # Option 3: Batch processing
    print("\n=== BATCH ===")
    files = ["doc1.txt", "doc2.txt", "doc3.txt"]
    questions = ["Summarize", "Extract numbers", "Find errors"]
    # batch_process_ocr(files, questions)