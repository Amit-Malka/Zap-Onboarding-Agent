import json
import logging
from typing import Any

try:
    from langchain_core.prompts import PromptTemplate
except ImportError:  # pragma: no cover
    PromptTemplate = None

try:
    from langchain_groq import ChatGroq
except ImportError:  # pragma: no cover
    ChatGroq = None

logger = logging.getLogger(__name__)

BUSINESS_DATA_FIELDS = (
    "business_name",
    "owner_name",
    "phone",
    "whatsapp",
    "address",
    "area",
    "category",
    "services",
    "service_areas",
    "working_hours",
    "rating",
    "review_count",
    "about_text",
    "source_url",
    "has_personal_website",
)


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


def extract_business_data(raw_text: str, source_url: str) -> dict[str, Any]:
    if PromptTemplate is None or ChatGroq is None:
        raise ImportError("Missing LangChain/Groq dependencies for business extraction")

    prompt = PromptTemplate(
        input_variables=["raw_text", "source_url"],
        template=(
            "You are an information extraction system.\n"
            "Extract business information from the provided raw text.\n"
            "Return ONLY a valid JSON object with no markdown and no extra text.\n"
            "Use exactly this schema and keys:\n"
            "{\n"
            '  "business_name": str,\n'
            '  "owner_name": str or null,\n'
            '  "phone": str,\n'
            '  "whatsapp": str or null,\n'
            '  "address": str,\n'
            '  "area": str,\n'
            '  "category": str,\n'
            '  "services": list[str],\n'
            '  "service_areas": list[str],\n'
            '  "working_hours": str,\n'
            '  "rating": str or null,\n'
            '  "review_count": int or null,\n'
            '  "about_text": str or null,\n'
            '  "source_url": str,\n'
            '  "has_personal_website": bool\n'
            "}\n\n"
            "Raw text:\n{raw_text}\n\n"
            "Source URL:\n{source_url}\n"
        ),
    )

    chain = prompt | ChatGroq(model="qwen/qwen3-32b")
    response = chain.invoke({"raw_text": raw_text, "source_url": source_url})
    response_text = response if isinstance(response, str) else getattr(response, "content", "")

    try:
        parsed = json.loads(response_text)
        return parsed if isinstance(parsed, dict) else _null_business_data(source_url)
    except (json.JSONDecodeError, TypeError) as error:
        logger.error("Failed to parse business extraction JSON: %s", error)
        return _null_business_data(source_url)


def _null_business_data(source_url: str) -> dict[str, Any]:
    result = {field: None for field in BUSINESS_DATA_FIELDS}
    result["source_url"] = source_url
    return result
