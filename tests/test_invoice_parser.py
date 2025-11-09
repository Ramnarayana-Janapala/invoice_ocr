"""
Tests for invoice parser - validates parsing and data structure.
"""
import pytest
from dataclasses import dataclass
from typing import List, Optional
from paddleocr_app.invoice_parser import (
    Invoice,
    BillingInformation,
    ShippingInformation,
    LineItem,
    Address,
    Contact,
    InvoiceSummary,
    InvoiceParser,
    parse_invoice,
)


# ============================================================================
# MOCK OCRResult to simulate PaddleOCR output
# ============================================================================

@dataclass
class MockOCRResult:
    """Mock OCRResult matching PaddleOCREngine.OCRResult structure."""
    text: str
    confidence: float
    bbox: Optional[List[List[float]]] = None
    raw_result: Optional[dict] = None


# ============================================================================
# TEST DATA - Real invoice from the document
# ============================================================================

SAMPLE_OCR_RESULTS = [
    MockOCRResult("06/10/2021", 0.9999),
    MockOCRResult("Company", 0.9898),
    MockOCRResult("Sample Invoice", 0.9993),
    MockOCRResult("INVO-005", 0.9965),
    MockOCRResult("Billing Information", 0.9998),
    MockOCRResult("Shipping Information", 0.9995),
    MockOCRResult("Company", 0.9999),
    MockOCRResult("ABC Company", 0.9976),
    MockOCRResult("Name", 0.9999),
    MockOCRResult("John Smith", 0.9514),
    MockOCRResult("Name", 0.9999),
    MockOCRResult("Sam K. Smith", 0.9991),
    MockOCRResult("Address", 0.9999),
    MockOCRResult("111 Pine Street, Suite 1815, San Francisco, CA, 94111", 0.9621),
    MockOCRResult("Address", 0.9999),
    MockOCRResult("111 Pine Street, Suite 1815, San Francisco, CA, 94111", 0.9629),
    MockOCRResult("Phone Number", 0.9988),
    MockOCRResult("(123) 123-1232", 0.9990),
    MockOCRResult("Email", 0.9085),
    MockOCRResult("John@example.com", 0.9998),
    MockOCRResult("Description", 0.9999),
    MockOCRResult("Quantity", 0.9999),
    MockOCRResult("Unit Price", 0.9444),
    MockOCRResult("Total", 0.9999),
    MockOCRResult("Product/Service 1", 0.9880),
    MockOCRResult("Sink", 0.9999),
    MockOCRResult("2", 0.9998),
    MockOCRResult("100", 0.9999),
    MockOCRResult("$200", 0.9998),
    MockOCRResult("Product/Service 2", 0.9923),
    MockOCRResult("Nest Smart Filter", 0.9998),
    MockOCRResult("1", 0.9999),
    MockOCRResult("150", 0.9999),
    MockOCRResult("$150", 0.9999),
    MockOCRResult("Product/Service 3", 0.9991),
    MockOCRResult("Labor Fee", 0.9434),
    MockOCRResult("1", 0.9999),
    MockOCRResult("50", 0.9999),
    MockOCRResult("$50", 0.9999),
    MockOCRResult("Product/Service 4", 0.9987),
    MockOCRResult("Service Fee", 0.9998),
    MockOCRResult("1", 0.9999),
    MockOCRResult("25", 0.9999),
    MockOCRResult("$25", 0.9998),
    MockOCRResult("Total:", 0.9991),
    MockOCRResult("$425", 0.9999),
]


# ============================================================================
# UNIT TESTS - Test individual components
# ============================================================================

class TestAddressModel:
    """Test Address model validation."""

    def test_address_creation(self):
        """Test creating valid address."""
        addr = Address(
            street="111 Pine Street, Suite 1815",
            city="San Francisco",
            state="CA",
            zip_code="94111",
        )
        assert addr.street == "111 Pine Street, Suite 1815"
        assert addr.city == "San Francisco"
        assert addr.state == "CA"
        assert addr.zip_code == "94111"

    def test_address_whitespace_stripping(self):
        """Test whitespace is stripped."""
        addr = Address(
            street="  111 Pine Street  ",
            city="  San Francisco  ",
        )
        assert addr.street == "111 Pine Street"
        assert addr.city == "San Francisco"


class TestContactModel:
    """Test Contact model validation."""

    def test_contact_with_all_fields(self):
        """Test contact with phone and email."""
        contact = Contact(
            phone_number="(123) 123-1232",
            email="john@example.com",
        )
        assert contact.phone_number == "(123) 123-1232"
        assert contact.email == "john@example.com"

    def test_contact_optional_fields(self):
        """Test contact with optional fields."""
        contact = Contact()
        assert contact.phone_number is None
        assert contact.email is None


class TestLineItemModel:
    """Test LineItem model validation."""

    def test_line_item_creation(self):
        """Test creating valid line item."""
        item = LineItem(
            item_id=1,
            product_service="Product/Service 1",
            description="Sink",
            quantity=2,
            unit_price=100,
            total=200,
        )
        assert item.item_id == 1
        assert item.quantity == 2
        assert item.unit_price == 100
        assert item.total == 200

    def test_line_item_quantity_validation(self):
        """Test quantity must be > 0."""
        with pytest.raises(ValueError):
            LineItem(
                item_id=1,
                product_service="Product",
                description="Test",
                quantity=0,
                unit_price=100,
                total=0,
            )

    def test_line_item_price_validation(self):
        """Test price must be > 0."""
        with pytest.raises(ValueError):
            LineItem(
                item_id=1,
                product_service="Product",
                description="Test",
                quantity=1,
                unit_price=-10,
                total=0,
            )


class TestInvoiceSummaryModel:
    """Test InvoiceSummary model validation."""

    def test_summary_creation(self):
        """Test creating valid summary."""
        summary = InvoiceSummary(
            subtotal=425,
            tax=0,
            total=425,
            currency="USD",
        )
        assert summary.subtotal == 425
        assert summary.tax == 0
        assert summary.total == 425
        assert summary.currency == "USD"

    def test_summary_with_tax(self):
        """Test summary with tax."""
        summary = InvoiceSummary(
            subtotal=400,
            tax=50,
            total=450,
            currency="USD",
        )
        assert summary.total == 450


class TestBillingInformationModel:
    """Test BillingInformation model."""

    def test_billing_creation(self):
        """Test creating valid billing info."""
        billing = BillingInformation(
            company="ABC Company",
            name="John Smith",
            address=Address(
                street="111 Pine Street, Suite 1815",
                city="San Francisco",
                state="CA",
                zip_code="94111",
            ),
            contact=Contact(
                phone_number="(123) 123-1232",
                email="john@example.com",
            ),
        )
        assert billing.company == "ABC Company"
        assert billing.name == "John Smith"
        assert billing.address.city == "San Francisco"
        assert billing.contact.email == "john@example.com"


class TestInvoiceModel:
    """Test complete Invoice model."""

    def test_invoice_creation(self):
        """Test creating valid invoice."""
        line_items = [
            LineItem(
                item_id=1,
                product_service="Product/Service 1",
                description="Sink",
                quantity=2,
                unit_price=100,
                total=200,
            ),
        ]

        invoice = Invoice(
            date="06/10/2021",
            invoice_number="INVO-005",
            company_name="Company Name",
            billing_information=BillingInformation(
                company="ABC Company",
                name="John Smith",
                address=Address(street="111 Pine Street", city="San Francisco"),
                contact=Contact(email="john@example.com"),
            ),
            shipping_information=ShippingInformation(
                name="Sam K. Smith",
                address=Address(street="111 Pine Street", city="San Francisco"),
            ),
            line_items=line_items,
            summary=InvoiceSummary(subtotal=200, tax=0, total=200),
        )

        assert invoice.invoice_number == "INVO-005"
        assert len(invoice.line_items) == 1
        assert invoice.summary.total == 200


# ============================================================================
# INTEGRATION TESTS - Test parser with real OCR data
# ============================================================================

class TestInvoiceParser:
    """Test invoice parser functionality."""

    def test_parser_initialization(self):
        """Test parser initializes correctly."""
        parser = InvoiceParser()
        assert parser is not None


    def test_parse_address(self):
        """Test address parsing."""
        parser = InvoiceParser()
        address_str = "111 Pine Street Suite 1815, San Francisco, CA, 94111"

        addr = parser.parse_address(address_str)
        assert addr.street == "111 Pine Street Suite 1815"
        assert addr.city == "San Francisco"
        assert addr.state == "CA"
        assert addr.zip_code == "94111"

    def test_parse_line_items(self):
        """Test line items extraction."""
        parser = InvoiceParser()

        ocr_results = [
            MockOCRResult("Product/Service 1", 0.99),
            MockOCRResult("Sink", 0.99),
            MockOCRResult("2", 0.99),
            MockOCRResult("100", 0.99),
            MockOCRResult("$200", 0.99),
        ]

        items = parser.parse_line_items(ocr_results)
        assert len(items) == 1
        assert items[0].description == "Sink"
        assert items[0].quantity == 2
        assert items[0].unit_price == 100
        assert items[0].total == 200

    def test_parse_invoice_convenience_function(self):
        """Test convenience parse_invoice function."""
        invoice = parse_invoice(SAMPLE_OCR_RESULTS)
        assert invoice is not None
        assert invoice.invoice_number == "INVO-005"


class TestInvoiceSerialization:
    """Test invoice serialization."""

    def test_invoice_to_dict(self):
        """Test converting invoice to dict."""
        line_items = [
            LineItem(
                item_id=1,
                product_service="Product/Service 1",
                description="Sink",
                quantity=2,
                unit_price=100,
                total=200,
            ),
        ]

        invoice = Invoice(
            date="06/10/2021",
            invoice_number="INVO-005",
            company_name="Company Name",
            billing_information=BillingInformation(
                company="ABC Company",
                name="John Smith",
                address=Address(street="111 Pine Street", city="San Francisco"),
                contact=Contact(email="john@example.com"),
            ),
            shipping_information=ShippingInformation(
                name="Sam K. Smith",
                address=Address(street="111 Pine Street", city="San Francisco"),
            ),
            line_items=line_items,
            summary=InvoiceSummary(subtotal=200, tax=0, total=200),
        )

        invoice_dict = invoice.dict()
        assert isinstance(invoice_dict, dict)
        assert invoice_dict['invoice_number'] == "INVO-005"
        assert invoice_dict['summary']['total'] == 200


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """Run tests with: pytest test_invoice_parser.py -v"""
    print("Run tests with: pytest test_invoice_parser.py -v")
    print("\nExample usage:")
    print("  from invoice_parser import parse_invoice")
    print("  invoice = parse_invoice(ocr_results)")
    print("  print(invoice.dict())")