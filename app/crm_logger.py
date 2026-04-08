import json
import logging
import os
from typing import Any

try:
    import gspread
except ModuleNotFoundError:
    gspread = None

try:
    from oauth2client.service_account import ServiceAccountCredentials
except ModuleNotFoundError:
    ServiceAccountCredentials = None

LOGGER = logging.getLogger(__name__)

CRM_HEADERS = [
    "card_id",
    "created_at",
    "business_name",
    "owner_name",
    "phone",
    "whatsapp",
    "address",
    "area",
    "services",
    "service_areas",
    "working_hours",
    "rating",
    "source_url",
    "has_personal_website",
    "onboarding_script",
]


def _join_list(value: Any) -> str:
    if not isinstance(value, list):
        return ""
    return ", ".join(str(item) for item in value if item is not None)


def log_to_crm(customer_card: dict, onboarding_script: str) -> bool:
    if gspread is None or ServiceAccountCredentials is None:
        LOGGER.error("Missing gspread or oauth2client dependency")
        return False

    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")

    if not service_account_json or not spreadsheet_id:
        LOGGER.error("Missing GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SHEETS_SPREADSHEET_ID")
        return False

    try:
        credentials_dict = json.loads(service_account_json)
    except Exception as exc:
        LOGGER.exception("Failed to parse GOOGLE_SERVICE_ACCOUNT_JSON: %s", exc)
        return False

    try:
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scopes)
    except Exception as exc:
        LOGGER.exception("Failed to build Google credentials: %s", exc)
        return False

    try:
        client = gspread.authorize(credentials)
    except Exception as exc:
        LOGGER.exception("Failed to authorize gspread client: %s", exc)
        return False

    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
    except Exception as exc:
        LOGGER.exception("Failed to open spreadsheet by id: %s", exc)
        return False

    try:
        worksheet = spreadsheet.worksheet("Onboarding CRM")
    except Exception:
        try:
            worksheet = spreadsheet.add_worksheet(title="Onboarding CRM", rows="1000", cols="20")
        except Exception as exc:
            LOGGER.exception("Failed to get or create Onboarding CRM worksheet: %s", exc)
            return False

    try:
        header_row = worksheet.row_values(1)
        if not header_row:
            worksheet.append_row(CRM_HEADERS)
    except Exception as exc:
        LOGGER.exception("Failed to ensure CRM header row: %s", exc)
        return False

    try:
        row = [
            customer_card.get("card_id", ""),
            customer_card.get("created_at", ""),
            customer_card.get("business_name", ""),
            customer_card.get("owner_name", ""),
            customer_card.get("phone", ""),
            customer_card.get("whatsapp", ""),
            customer_card.get("address", ""),
            customer_card.get("area", ""),
            _join_list(customer_card.get("services")),
            _join_list(customer_card.get("service_areas")),
            customer_card.get("working_hours", ""),
            customer_card.get("rating", ""),
            customer_card.get("source_url", ""),
            customer_card.get("has_personal_website", ""),
            onboarding_script or "",
        ]
        worksheet.append_row(row)
    except Exception as exc:
        LOGGER.exception("Failed to append CRM row: %s", exc)
        return False

    return True
