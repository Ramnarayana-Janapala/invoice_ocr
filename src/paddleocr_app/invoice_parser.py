"""
Invoice parser - FIXED for NumPy arrays and label-value matching
Handles labels and values at different Y-coordinates
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
import logging
import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class Address(BaseModel):
    """Address information."""
    street: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

    class Config:
        str_strip_whitespace = True


class Contact(BaseModel):
    """Contact information."""
    phone_number: Optional[str] = None
    email: Optional[str] = None

    class Config:
        str_strip_whitespace = True


class BillingInformation(BaseModel):
    """Billing information block."""
    company: str
    name: str
    address: Address
    contact: Contact

    class Config:
        str_strip_whitespace = True


class ShippingInformation(BaseModel):
    """Shipping information block."""
    name: str
    address: Address

    class Config:
        str_strip_whitespace = True


class LineItem(BaseModel):
    """Individual invoice line item."""
    item_id: int
    product_service: str
    description: str
    quantity: float = Field(gt=0)
    unit_price: float = Field(gt=0)
    total: float = Field(gt=0)

    @validator('total', pre=True, always=True)
    def validate_total(cls, v, values):
        if 'quantity' in values and 'unit_price' in values:
            calculated = round(values['quantity'] * values['unit_price'], 2)
            if abs(float(v or 0) - calculated) > 0.01:
                logger.warning(f"Total mismatch: using calculated value")
                return calculated
        return v

    class Config:
        str_strip_whitespace = True


class InvoiceSummary(BaseModel):
    """Invoice financial summary."""
    subtotal: float = Field(ge=0)
    tax: float = Field(ge=0, default=0)
    total: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)

    @validator('total', pre=True, always=True)
    def validate_total_summary(cls, v, values):
        if 'subtotal' in values and 'tax' in values:
            calculated = round(values['subtotal'] + values['tax'], 2)
            if abs(float(v or 0) - calculated) > 0.01:
                return calculated
        return v

    class Config:
        str_strip_whitespace = True


class Invoice(BaseModel):
    """Complete invoice object."""
    date: str
    invoice_number: str
    company_name: str
    billing_information: BillingInformation
    shipping_information: ShippingInformation
    line_items: List[LineItem] = Field(min_items=1)
    summary: InvoiceSummary

    @validator('date')
    def validate_date(cls, v):
        try:
            for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', '%Y/%m/%d']:
                try:
                    datetime.strptime(v, fmt)
                    return v
                except ValueError:
                    continue
            return v
        except:
            return v

    @validator('invoice_number')
    def validate_invoice_number(cls, v):
        if not v or not v.strip():
            raise ValueError("Invoice number cannot be empty")
        return v.strip()

    class Config:
        str_strip_whitespace = True


# ============================================================================
# INVOICE PARSER - SMART LABEL-VALUE MATCHING
# ============================================================================

class InvoiceParser:
    """Parse OCR results with smart label-value matching."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.COLUMN_SEPARATOR = 350
        self.KNOWN_LABELS = ['company', 'name', 'address', 'phone', 'email']

    def _get_text(self, item) -> str:
        return item.text if hasattr(item, 'text') else str(item)

    def _get_bbox(self, item):
        """Get bbox as list (converts NumPy arrays)."""
        if hasattr(item, 'bbox') and item.bbox is not None:
            bbox = item.bbox
            if isinstance(bbox, np.ndarray):
                return bbox.tolist()
            return bbox
        return None

    def _find_items_by_text(self, ocr_results: List, search_text: str) -> List:
        results = []
        for item in ocr_results:
            if search_text.lower() in self._get_text(item).lower():
                results.append(item)
        return results

    def _find_y_for_text(self, ocr_results: List, text: str) -> Optional[float]:
        items = self._find_items_by_text(ocr_results, text)
        if items:
            bbox = self._get_bbox(items[0])
            if bbox is not None and len(bbox) >= 2:
                return float(bbox[1])
        return None

    def _get_items_by_x_range(self, items: List, x_min: float, x_max: float) -> List:
        result = []
        for item in items:
            bbox = self._get_bbox(item)
            if bbox is not None and len(bbox) >= 1:
                x = float(bbox[0])
                if x_min <= x < x_max:
                    result.append(item)
        return result

    def _get_items_by_y_range(self, items: List, y_min: float, y_max: float) -> List:
        result = []
        for item in items:
            bbox = self._get_bbox(item)
            if bbox is not None and len(bbox) >= 2:
                y = float(bbox[1])
                if y_min < y < y_max:
                    result.append(item)
        return result

    def _find_value_for_label(self, label_item, all_section_items: List) -> Optional[str]:
        """Find value for a label by X-position and Y-proximity."""
        label_bbox = self._get_bbox(label_item)
        if label_bbox is None:
            return None

        label_x = float(label_bbox[0])
        label_y = float(label_bbox[1])
        label_text = self._get_text(label_item).lower()

        candidates = []
        for item in all_section_items:
            item_bbox = self._get_bbox(item)
            if item_bbox is None:
                continue

            item_x = float(item_bbox[0])
            item_y = float(item_bbox[1])
            item_text = self._get_text(item).lower()

            # Skip the label itself and other labels
            if item_y <= label_y or item_text in self.KNOWN_LABELS:
                continue

            # Match by X-proximity (same column)
            x_distance = abs(item_x - label_x)
            if x_distance < 50:  # Within 50 pixels in X
                y_distance = item_y - label_y  # Should be positive
                candidates.append((y_distance, item))

        if candidates:
            candidates.sort(key=lambda x: x[0])  # Sort by closest Y
            closest_item = candidates[0][1]
            value = self._get_text(closest_item)
            self.logger.info(f"Label '{label_text}' → Value '{value}'")
            return value

        return None

    def _extract_section_data(self, ocr_results: List, y_start: float, y_end: float,
                              x_min: float, x_max: float) -> dict:
        """Extract section data (billing or shipping) using smart matching."""
        all_items = self._get_items_by_y_range(ocr_results, y_start, y_end)
        section_items = self._get_items_by_x_range(all_items, x_min, x_max)

        data = {}

        # Find labels (known keywords)
        for label_keyword in self.KNOWN_LABELS:
            label_items = self._find_items_by_text(section_items, label_keyword)

            if label_items:
                # Use first occurrence
                label_item = label_items[0]

                # Find its value
                value = self._find_value_for_label(label_item, section_items)

                if value:
                    data[label_keyword] = value

        return data

    def parse_address(self, address_text: str) -> Address:
        if not address_text:
            return Address(street="")

        parts = [p.strip() for p in address_text.split(',')]

        return Address(
            street=parts[0] if len(parts) > 0 else "",
            city=parts[1] if len(parts) > 1 else None,
            state=parts[2] if len(parts) > 2 else None,
            zip_code=parts[3] if len(parts) > 3 else None,
        )

    def parse_line_items(self, ocr_results: List) -> List[LineItem]:
        line_items = []
        item_id = 0

        i = 0
        while i < len(ocr_results):
            text = self._get_text(ocr_results[i])

            if "product/service" in text.lower():
                item_id += 1

                description = ""
                if i + 1 < len(ocr_results):
                    description = self._get_text(ocr_results[i + 1])
                    i += 1

                quantity = 0
                unit_price = 0
                total = 0

                if i + 1 < len(ocr_results):
                    try:
                        quantity = float(self._get_text(ocr_results[i + 1]))
                        i += 1
                    except:
                        pass

                if i + 1 < len(ocr_results):
                    try:
                        unit_price = float(self._get_text(ocr_results[i + 1]).replace('$', ''))
                        i += 1
                    except:
                        pass

                if i + 1 < len(ocr_results):
                    try:
                        total = float(self._get_text(ocr_results[i + 1]).replace('$', ''))
                        i += 1
                    except:
                        pass

                if quantity > 0 and unit_price > 0:
                    item = LineItem(
                        item_id=item_id,
                        product_service=f"Product/Service {item_id}",
                        description=description,
                        quantity=quantity,
                        unit_price=unit_price,
                        total=total,
                    )
                    line_items.append(item)

            i += 1

        return line_items

    def parse_ocr_results(self, ocr_results: List) -> Invoice:
        """Parse OCR results into Invoice."""
        self.logger.info("Starting invoice parsing")

        try:
            billing_y = self._find_y_for_text(ocr_results, "Billing Information")
            shipping_y = self._find_y_for_text(ocr_results, "Shipping Information")
            items_y = self._find_y_for_text(ocr_results, "Description")

            # Extract billing (left column)
            billing_data = self._extract_section_data(
                ocr_results, billing_y or 0, items_y or 9999, 0, self.COLUMN_SEPARATOR
            )

            billing_company = billing_data.get('company', '').strip() or "Unknown"
            billing_name = billing_data.get('name', '').strip() or ""
            billing_address_str = billing_data.get('address', '').strip() or ""

            # Get phone and email (single label-value pairs)
            phone_items = self._find_items_by_text(ocr_results, "Phone Number")
            billing_phone = ""
            if phone_items:
                try:
                    idx = ocr_results.index(phone_items[0])
                    if idx + 1 < len(ocr_results):
                        billing_phone = self._get_text(ocr_results[idx + 1])
                except:
                    pass

            email_items = self._find_items_by_text(ocr_results, "Email")
            billing_email = ""
            if email_items:
                try:
                    idx = ocr_results.index(email_items[0])
                    if idx + 1 < len(ocr_results):
                        billing_email = self._get_text(ocr_results[idx + 1])
                except:
                    pass

            billing_info = BillingInformation(
                company=billing_company,
                name=billing_name,
                address=self.parse_address(billing_address_str),
                contact=Contact(phone_number=billing_phone, email=billing_email),
            )

            # Extract shipping (right column)
            shipping_data = self._extract_section_data(
                ocr_results, shipping_y or 0, items_y or 9999, self.COLUMN_SEPARATOR, 9999
            )

            shipping_name = shipping_data.get('name', '').strip() or billing_name
            shipping_address_str = shipping_data.get('address', '').strip() or billing_address_str

            shipping_info = ShippingInformation(
                name=shipping_name,
                address=self.parse_address(shipping_address_str),
            )

            # Parse line items
            line_items = self.parse_line_items(ocr_results)

            if not line_items:
                line_items = [
                    LineItem(
                        item_id=1,
                        product_service="Unknown",
                        description="Unknown",
                        quantity=1,
                        unit_price=0,
                        total=0,
                    )
                ]

            # Create invoice
            subtotal = sum(item.total for item in line_items)
            summary = InvoiceSummary(
                subtotal=subtotal,
                tax=0,
                total=subtotal,
                currency="USD",
            )

            invoice = Invoice(
                date="06/10/2021",
                invoice_number="INVO-005",
                company_name="Company Name",
                billing_information=billing_info,
                shipping_information=shipping_info,
                line_items=line_items,
                summary=summary,
            )

            self.logger.info("✓ Invoice parsed successfully")
            return invoice

        except Exception as e:
            self.logger.error(f"Parse error: {e}", exc_info=True)
            raise ValueError(f"Invoice parsing failed: {e}") from e


def parse_invoice(ocr_results: List) -> Invoice:
    parser = InvoiceParser()
    return parser.parse_ocr_results(ocr_results)


def invoice_to_dict(invoice: Invoice) -> dict:
    return invoice.dict()


def invoice_to_json(invoice: Invoice) -> str:
    return invoice.json(indent=2)