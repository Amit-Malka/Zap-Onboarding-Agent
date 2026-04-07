from typing import Any


def extract_customer_profile(scraped_data: dict[str, Any]) -> dict[str, Any]:
    """Extract structured customer fields from raw scraped data."""
    if "content" not in scraped_data:
        raise ValueError("scraped_data must include 'content'")
    return {
        "company_name": "",
        "industry": "",
        "pain_points": [],
        "goals": [],
    }
