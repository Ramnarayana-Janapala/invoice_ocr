
from paddleocr_app.invoice_extraction import create_invoice_extractor
from pathlib import Path

# Create extractor
extractor = create_invoice_extractor(language="en")

# Extract from image
invoice = extractor.extract_from_image(Path("invoice.jpg"))

# Access structured data
print(f"Invoice: {invoice.invoice_number}")
print(f"Total: ${invoice.summary.total}")
print(f"Bill To: {invoice.billing_information.name}")

# Convert to dictionary for JSON/storage
invoice_dict = invoice.dict()
print(invoice_dict)