from app.card_generator import build_customer_card


def test_build_customer_card_maps_profile_fields() -> None:
    profile = {
        "company_name": "Acme Inc.",
        "industry": "SaaS",
        "pain_points": ["manual onboarding"],
        "goals": ["automation"],
    }
    card = build_customer_card(profile)
    assert card["title"] == "Acme Inc."
    assert card["industry"] == "SaaS"
    assert card["pain_points"] == ["manual onboarding"]
    assert card["goals"] == ["automation"]


def test_build_customer_card_uses_defaults_when_missing_fields() -> None:
    card = build_customer_card({})
    assert card["title"] == "Unknown Company"
    assert card["industry"] == "Unknown"
