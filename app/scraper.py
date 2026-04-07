import logging
from typing import Any

from crawl4ai import AsyncWebCrawler

logger = logging.getLogger(__name__)


def scrape_customer_website(url: str) -> dict[str, Any]:
    """Scrape a customer website and return normalized raw content."""
    if not url:
        raise ValueError("url is required")
    return {"url": url, "content": ""}


def _markdown_text_from_result(result: Any) -> str:
    markdown = getattr(result, "markdown", None)
    if markdown is None:
        return ""
    raw = getattr(markdown, "raw_markdown", None)
    if isinstance(raw, str):
        return raw
    return ""


async def scrape_digital_assets(dapayzahav_url: str) -> dict[str, str]:
    """Fetch a Dapay Zahav public profile page and return raw markdown content."""
    source = dapayzahav_url.strip() if dapayzahav_url else ""
    if not source:
        return {"dapayzahav_raw": "", "source_url": dapayzahav_url or ""}

    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=source)

        if not getattr(result, "success", False):
            err = getattr(result, "error_message", None) or "crawl unsuccessful"
            logger.error("Scrape failed for %s: %s", source, err)
            return {"dapayzahav_raw": "", "source_url": source}

        return {"dapayzahav_raw": _markdown_text_from_result(result), "source_url": source}
    except Exception:
        logger.exception("Scrape failed for %s", source)
        return {"dapayzahav_raw": "", "source_url": source}
