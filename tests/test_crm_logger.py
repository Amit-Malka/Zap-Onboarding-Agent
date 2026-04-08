import json

from app import crm_logger


def test_log_to_crm_creates_header_and_appends_row(monkeypatch) -> None:
    customer_card = {
        "card_id": "card-1",
        "created_at": "2026-04-08T10:00:00",
        "business_name": "Acme",
        "owner_name": "Amit",
        "phone": "111",
        "whatsapp": "222",
        "address": "Addr",
        "area": "Area",
        "services": ["S1", "S2"],
        "service_areas": ["A", "B"],
        "working_hours": "9-5",
        "rating": 4.5,
        "source_url": "https://example.com",
        "has_personal_website": True,
    }
    onboarding_script = "hello"
    env_json = '{"type":"service_account","project_id":"p"}'
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", env_json)
    monkeypatch.setenv("GOOGLE_SHEETS_SPREADSHEET_ID", "spreadsheet-id")

    class FakeSheet:
        def __init__(self):
            self.row1 = []
            self.appended = []

        def row_values(self, index):
            assert index == 1
            return self.row1

        def append_row(self, values):
            self.appended.append(values)

    class FakeSpreadsheet:
        def __init__(self, sheet):
            self.sheet = sheet

        def worksheet(self, name):
            assert name == "Onboarding CRM"
            raise Exception("not found")

        def add_worksheet(self, title, rows, cols):
            assert title == "Onboarding CRM"
            assert rows == "1000"
            assert cols == "20"
            return self.sheet

    class FakeClient:
        def __init__(self, sheet):
            self.sheet = sheet

        def open_by_key(self, key):
            assert key == "spreadsheet-id"
            return FakeSpreadsheet(self.sheet)

    class FakeCreds:
        @staticmethod
        def from_json_keyfile_dict(payload, scope):
            assert payload["project_id"] == "p"
            assert "https://www.googleapis.com/auth/spreadsheets" in scope
            return object()

    fake_sheet = FakeSheet()

    class FakeGspread:
        @staticmethod
        def authorize(_creds):
            return FakeClient(fake_sheet)

    monkeypatch.setattr(crm_logger, "ServiceAccountCredentials", FakeCreds)
    monkeypatch.setattr(crm_logger, "gspread", FakeGspread)

    result = crm_logger.log_to_crm(customer_card, onboarding_script)

    assert result is True
    assert fake_sheet.appended[0][0] == "card_id"
    assert fake_sheet.appended[1][0] == "card-1"
    assert fake_sheet.appended[1][8] == "S1, S2"
    assert fake_sheet.appended[1][9] == "A, B"
    assert fake_sheet.appended[1][-1] == "hello"


def test_log_to_crm_returns_false_on_missing_env(monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_JSON", raising=False)
    monkeypatch.delenv("GOOGLE_SHEETS_SPREADSHEET_ID", raising=False)

    result = crm_logger.log_to_crm({}, "script")
    assert result is False


def test_log_to_crm_returns_false_on_bad_credentials_json(monkeypatch) -> None:
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{")
    monkeypatch.setenv("GOOGLE_SHEETS_SPREADSHEET_ID", "spreadsheet-id")

    result = crm_logger.log_to_crm({}, "script")
    assert result is False
