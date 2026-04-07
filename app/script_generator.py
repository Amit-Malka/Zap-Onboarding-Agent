from typing import Any


def generate_onboarding_script(card: dict[str, Any]) -> str:
    """Generate a short onboarding script from a customer card."""
    company_name = card.get("title", "the customer")
    return f"Welcome to Zap, {company_name}. Let's start your onboarding."
