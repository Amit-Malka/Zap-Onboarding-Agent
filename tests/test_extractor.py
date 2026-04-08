from app.extractor import extract_customer_profile


def test_extract_customer_profile_returns_expected_keys() -> None:
    profile = extract_customer_profile({"content": "Example data"})
    assert "company_name" in profile
    assert "industry" in profile
    assert "pain_points" in profile
    assert "goals" in profile


def test_extract_customer_profile_requires_content_field() -> None:
    try:
        extract_customer_profile({})
        assert False
    except ValueError:
        assert True


def test_extract_business_data_returns_parsed_json(monkeypatch) -> None:
    from app import extractor

    class FakeChain:
        def invoke(self, payload):
            assert "raw_text" in payload
            assert "source_url" in payload
            return (
                '{"business_name":"A","owner_name":null,"phone":"123","whatsapp":null,'
                '"address":"Addr","area":"Area","category":"Cat","services":["S1"],'
                '"service_areas":["SA"],"working_hours":"9-5","rating":null,'
                '"review_count":null,"about_text":null,"source_url":"https://x.com",'
                '"has_personal_website":false}'
            )

    class FakePrompt:
        def __init__(self, *args, **kwargs):
            pass

        def __or__(self, _llm):
            return FakeChain()

    class FakeChatGroq:
        def __init__(self, *args, **kwargs):
            assert kwargs["model"] == "qwen/qwen3-32b"

    monkeypatch.setattr(extractor, "PromptTemplate", FakePrompt)
    monkeypatch.setattr(extractor, "ChatGroq", FakeChatGroq)

    result = extractor.extract_business_data("raw", "https://x.com")
    assert result["business_name"] == "A"
    assert result["services"] == ["S1"]
    assert result["source_url"] == "https://x.com"
    assert result["has_personal_website"] is False


def test_extract_business_data_returns_null_fallback_on_bad_json(monkeypatch) -> None:
    from app import extractor

    class FakeChain:
        def invoke(self, _payload):
            return "not a json"

    class FakePrompt:
        def __init__(self, *args, **kwargs):
            pass

        def __or__(self, _llm):
            return FakeChain()

    class FakeChatGroq:
        def __init__(self, *args, **kwargs):
            assert kwargs["model"] == "qwen/qwen3-32b"

    monkeypatch.setattr(extractor, "PromptTemplate", FakePrompt)
    monkeypatch.setattr(extractor, "ChatGroq", FakeChatGroq)

    result = extractor.extract_business_data("raw", "https://source.example")
    assert result == {
        "business_name": None,
        "owner_name": None,
        "phone": None,
        "whatsapp": None,
        "address": None,
        "area": None,
        "category": None,
        "services": None,
        "service_areas": None,
        "working_hours": None,
        "rating": None,
        "review_count": None,
        "about_text": None,
        "source_url": "https://source.example",
        "has_personal_website": None,
    }


def test_extract_business_data_parses_json_inside_markdown_block(monkeypatch) -> None:
    from app import extractor

    class FakeResponse:
        content = (
            "```json\n"
            '{"business_name":"A","owner_name":null,"phone":"123","whatsapp":null,'
            '"address":"Addr","area":"Area","category":"Cat","services":["S1"],'
            '"service_areas":["SA"],"working_hours":"9-5","rating":null,'
            '"review_count":null,"about_text":null,"source_url":"https://x.com",'
            '"has_personal_website":false}\n'
            "```"
        )

    class FakeChain:
        def invoke(self, _payload):
            return FakeResponse()

    class FakePrompt:
        def __init__(self, *args, **kwargs):
            pass

        def __or__(self, _llm):
            return FakeChain()

    class FakeChatGroq:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(extractor, "PromptTemplate", FakePrompt)
    monkeypatch.setattr(extractor, "ChatGroq", FakeChatGroq)

    result = extractor.extract_business_data("raw", "https://x.com")

    assert result["business_name"] == "A"
    assert result["services"] == ["S1"]
