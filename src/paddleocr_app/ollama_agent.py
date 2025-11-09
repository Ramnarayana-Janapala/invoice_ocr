import requests
import json
from pathlib import Path


class OllamaOCRAgent:
    def __init__(self, model="mistral", url="http://localhost:11434/api/generate"):
        self.model = model
        self.url = url

    def query(self, ocr_data, question, stream=False):
        """Query with automatic error handling"""
        try:
            payload = {
                "model": self.model,
                "prompt": f"DOCUMENT:\n{ocr_data}\n\nQUESTION: {question}\n\nANSWER:",
                "stream": stream
            }
            response = requests.post(self.url, json=payload, timeout=60)
            response.raise_for_status()

            if stream:
                return self._handle_stream(response)
            else:
                return response.json()['response'].strip()
        except requests.exceptions.ConnectionError:
            return "❌ Error: Ollama not running. Start: ollama serve"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def _handle_stream(self, response):
        """Handle streaming response"""
        full = ""
        for line in response.iter_lines():
            if line:
                full += json.loads(line).get('response', '')
        return full

    def from_file(self, ocr_path, question):
        """Load OCR from file and query"""
        ocr_data = Path(ocr_path).read_text(encoding='utf-8')
        return self.query(ocr_data, question)

    def batch_questions(self, ocr_data, questions):
        """Ask multiple questions on same doc"""
        return {q: self.query(ocr_data, q) for q in questions}


# ============= QUICK START =============
if __name__ == "__main__":
    agent = OllamaOCRAgent(model="mistral")

    # Load OCR data
    ocr_text = "Invoice #123\nDate: 2025-01-15\nTotal: $500\nItems: Widget A, Widget B"

    # Single query
    result = agent.query(ocr_text, "What is the invoice total?")
    print(f"Answer: {result}")

    # Multiple queries
    answers = agent.batch_questions(ocr_text, [
        "Extract the invoice number",
        "What items are listed?",
        "When is this invoice dated?"
    ])

    for q, a in answers.items():
        print(f"\nQ: {q}")
        print(f"A: {a}")