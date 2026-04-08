from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def build_customer_card(extracted_data: dict[str, Any]) -> dict[str, Any]:
    """Build a customer card with metadata and missing fields."""
    missing_fields = [
        field_name
        for field_name, field_value in extracted_data.items()
        if field_value is None
    ]
    return {
        "card_id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        **extracted_data,
        "missing_fields": missing_fields,
    }
