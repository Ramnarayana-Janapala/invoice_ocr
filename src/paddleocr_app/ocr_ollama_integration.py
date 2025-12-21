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

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        result = response.json()
        
        # Handle different response formats
        if 'response' in result:
            return result['response']
        elif 'message' in result:
            # Some Ollama versions use 'message' instead of 'response'
            if isinstance(result['message'], dict):
                return result['message'].get('content', str(result))
            return str(result['message'])
        else:
            # Fallback: return the whole response as string
            raise ValueError(f"Unexpected response format from Ollama. Keys: {list(result.keys())}. Full response: {result}")
            
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Could not connect to Ollama at {OLLAMA_URL}. "
            "Make sure Ollama is running: 'ollama serve'"
        )
    except requests.exceptions.Timeout:
        raise TimeoutError(f"Request to Ollama timed out after 120 seconds")
    except requests.exceptions.HTTPError as e:
        error_text = response.text if hasattr(response, 'text') else 'N/A'
        raise ValueError(f"Ollama API error: {e}. Response: {error_text}")
    except json.JSONDecodeError as e:
        error_text = response.text if hasattr(response, 'text') else 'N/A'
        raise ValueError(f"Invalid JSON response from Ollama: {error_text}")


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