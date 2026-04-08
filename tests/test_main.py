from fastapi.testclient import TestClient

from app.main import app


def test_get_index_serves_single_page() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Run Onboarding" in response.text


def test_run_onboarding_success(monkeypatch) -> None:
    client = TestClient(app)

    async def fake_scrape(url: str):
        return {"dapayzahav_raw": "raw markdown", "source_url": url}

    def fake_extract(raw_text: str, source_url: str):
        assert raw_text == "raw markdown"
        assert source_url == "https://example.com/business"
        return {"business_name": "Acme", "owner_name": None}

    def fake_build_card(extracted_data):
        assert extracted_data == {"business_name": "Acme", "owner_name": None}
        return {
            "card_id": "card-1",
            "business_name": "Acme",
            "owner_name": None,
            "missing_fields": ["owner_name"],
        }

    def fake_generate_script(customer_card):
        assert customer_card["card_id"] == "card-1"
        return "## Opening\nHello"

    def fake_log_to_crm(customer_card, onboarding_script: str):
        assert customer_card["card_id"] == "card-1"
        assert onboarding_script == "## Opening\nHello"
        return True

    monkeypatch.setattr("app.main.scrape_digital_assets", fake_scrape)
    monkeypatch.setattr("app.main.extract_business_data", fake_extract)
    monkeypatch.setattr("app.main.build_customer_card", fake_build_card)
    monkeypatch.setattr("app.main.generate_onboarding_script", fake_generate_script)
    monkeypatch.setattr("app.main.log_to_crm", fake_log_to_crm)

    response = client.post(
        "/run-onboarding",
        json={"dapayzahav_url": "https://example.com/business"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "customer_card": {
            "card_id": "card-1",
            "business_name": "Acme",
            "owner_name": None,
            "missing_fields": ["owner_name"],
        },
        "onboarding_script": "## Opening\nHello",
        "crm_logged": True,
        "missing_fields": ["owner_name"],
    }


def test_run_onboarding_failure_returns_500(monkeypatch) -> None:
    client = TestClient(app)

    async def fake_scrape(url: str):
        return {"dapayzahav_raw": "raw markdown", "source_url": url}

    def fake_extract(_raw_text: str, _source_url: str):
        raise RuntimeError("extractor failed to parse")

    monkeypatch.setattr("app.main.scrape_digital_assets", fake_scrape)
    monkeypatch.setattr("app.main.extract_business_data", fake_extract)

    response = client.post("/run-onboarding", json={"dapayzahav_url": "https://example.com"})

    assert response.status_code == 500
    assert response.json()["detail"] == "Onboarding failed at extractor: extractor failed to parse"
