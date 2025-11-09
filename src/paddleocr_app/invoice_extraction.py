"""
High-level invoice extraction combining OCR and parsing.
"""
from pathlib import Path
from typing import Optional
import logging

from paddleocr_app.ocr import PaddleOCREngine, create_ocr_engine
from paddleocr_app.invoice_parser import (
    Invoice,
    InvoiceParser,
    parse_invoice,
)

logger = logging.getLogger(__name__)


class InvoiceExtractor:
    """
    End-to-end invoice extraction pipeline.
    Combines OCR processing with structured data parsing.
    """

    def __init__(self, language: str = "en"):
        """Initialize OCR engine and parser."""
        self.ocr_engine = create_ocr_engine(language=language)
        self.parser = InvoiceParser()
        self.logger = logging.getLogger(__name__)

    def extract_from_image(self, image_path: Path) -> Invoice:
        """
        Extract and parse invoice from image file.

        Args:
            image_path: Path to invoice image

        Returns:
            Structured and validated Invoice object

        Raises:
            FileNotFoundError: If image doesn't exist
            ValueError: If parsing fails
        """
        self.logger.info(f"Extracting invoice from: {image_path}")

        # Step 1: Run OCR
        ocr_results = self.ocr_engine.process_image(image_path)
        self.logger.info(f"OCR extracted {len(ocr_results)} text blocks")

        # Step 2: Parse into structured format
        invoice = self.parser.parse_ocr_results(ocr_results)
        self.logger.info("✓ Invoice extracted and validated")

        return invoice

    def extract_from_batch(self, image_dir: Path) -> dict:
        """
        Extract invoices from multiple images.

        Args:
            image_dir: Directory containing invoice images

        Returns:
            Dict mapping image paths to Invoice objects (or errors)
        """
        self.logger.info(f"Batch processing invoices from: {image_dir}")

        results = {}
        image_dir = Path(image_dir)

        for image_path in image_dir.glob("*.jpg"):
            try:
                invoice = self.extract_from_image(image_path)
                results[str(image_path)] = invoice
                self.logger.info(f"✓ {image_path.name}: Invoice {invoice.invoice_number}")
            except Exception as e:
                self.logger.error(f"✗ {image_path.name}: {e}")
                results[str(image_path)] = None

        return results


def create_invoice_extractor(language: str = "en") -> InvoiceExtractor:
    """Factory function to create invoice extractor."""
    return InvoiceExtractor(language=language)