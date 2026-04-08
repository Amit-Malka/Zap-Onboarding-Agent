from datetime import datetime
from uuid import UUID

from app.card_generator import build_customer_card


def test_build_customer_card_adds_metadata_and_missing_fields() -> None:
    extracted_data = {
        "business_name": "Acme Inc.",
        "owner_name": None,
        "industry": "SaaS",
        "phone": "03-5551234",
        "email": None,
    }

    card = build_customer_card(extracted_data)

    assert UUID(card["card_id"])
    datetime.fromisoformat(card["created_at"])
    assert card["business_name"] == "Acme Inc."
    assert card["industry"] == "SaaS"
    assert card["phone"] == "03-5551234"
    assert card["owner_name"] is None
    assert card["email"] is None
    assert set(card["missing_fields"]) == {"owner_name", "email"}
