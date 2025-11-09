from pathlib import Path

import requests
import json
import typer

from paddleocr_app.invoice_extraction import create_invoice_extractor

app = typer.Typer()
# ============= CONFIG =============
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"


# ============= 1. LOAD OCR DATA =============
def load_ocr_data(file_path):
    """Load extracted OCR text"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


# ============= 2. SEND TO MISTRAL =============
def query_mistral(ocr_data, question):
    """Send OCR data + question to Mistral"""
    prompt = f"""You are analyzing extracted document text.

DOCUMENT TEXT:
{ocr_data}

QUESTION:
{question}

ANSWER:"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.7
    }

    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()['response']


@app.command()
def extract_invoice(image_path: Path = typer.Argument(..., help="Path to invoice image"),
                    question: str = typer.Option(..., help="Question to ask about invoice")):
    """Extract and parse invoice from image."""
    extractor = create_invoice_extractor()

    try:
        invoice = extractor.extract_from_image(image_path)
        answer = query_mistral(invoice.json(), question)
        print(f"\n📋 OCR Text:\n{invoice.json()}")
        print(f"\n❓ Question: {question}")
        print(f"\n✅ Answer: {answer}")

    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)
        raise typer.Exit(1)


# ============= 3. MAIN WORKFLOW =============
def main():
   app()


if __name__ == "__main__":
    main()