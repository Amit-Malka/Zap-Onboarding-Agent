from typing import Any


def log_to_crm(record: dict[str, Any]) -> bool:
    """Log onboarding output to CRM (Google Sheets in future implementation)."""
    if not record:
        raise ValueError("record is required")
    return True
