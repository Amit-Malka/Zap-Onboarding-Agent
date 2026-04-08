import sys
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Stubs crawl4ai so importing app.scraper does not require the real package (e.g. CI / smoke runs).
_crawl4ai_stub = types.ModuleType("crawl4ai")
_crawl4ai_stub.AsyncWebCrawler = MagicMock()
sys.modules.setdefault("crawl4ai", _crawl4ai_stub)

from app.scraper import scrape_digital_assets


@pytest.mark.asyncio
async def test_scrape_digital_assets_returns_expected_keys() -> None:
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.markdown = MagicMock(raw_markdown="# Profile\nContent here.")

    mock_crawler = MagicMock()
    mock_crawler.arun = AsyncMock(return_value=mock_result)
    mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
    mock_crawler.__aexit__ = AsyncMock(return_value=None)

    url = "https://www.dapayzahav.co.il/example"
    with patch("app.scraper.AsyncWebCrawler", return_value=mock_crawler):
        out = await scrape_digital_assets(url)

    assert isinstance(out, dict)
    assert set(out.keys()) == {"dapayzahav_raw", "source_url"}
    assert out["source_url"] == url
    assert out["dapayzahav_raw"] == "# Profile\nContent here."
    mock_crawler.arun.assert_awaited_once_with(url=url)


@pytest.mark.asyncio
async def test_scrape_digital_assets_falls_back_to_http_fetch(monkeypatch) -> None:
    from app import scraper

    mock_crawler = MagicMock()
    mock_crawler.__aenter__ = AsyncMock(side_effect=NotImplementedError())
    mock_crawler.__aexit__ = AsyncMock(return_value=None)

    class FakeHttpResponse:
        status_code = 200
        text = "<html><body><h1>Business Name</h1><p>Plumbing in Tel Aviv</p></body></html>"

        def raise_for_status(self):
            return None

    monkeypatch.setattr(scraper, "AsyncWebCrawler", MagicMock(return_value=mock_crawler))
    monkeypatch.setattr(scraper.requests, "get", lambda *_args, **_kwargs: FakeHttpResponse())

    out = await scraper.scrape_digital_assets("https://www.d.co.il/example")

    assert out["source_url"] == "https://www.d.co.il/example"
    assert "Business Name" in out["dapayzahav_raw"]
