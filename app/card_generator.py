from typing import Any


def build_customer_card(profile: dict[str, Any]) -> dict[str, Any]:
    """Build a customer onboarding card from extracted profile data."""
    return {
        "title": profile.get("company_name", "Unknown Company"),
        "industry": profile.get("industry", "Unknown"),
        "pain_points": profile.get("pain_points", []),
        "goals": profile.get("goals", []),
    }
