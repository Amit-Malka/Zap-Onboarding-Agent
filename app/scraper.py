from typing import Any


def scrape_customer_website(url: str) -> dict[str, Any]:
    """Scrape a customer website and return normalized raw content."""
    if not url:
        raise ValueError("url is required")
    return {"url": url, "content": ""}
