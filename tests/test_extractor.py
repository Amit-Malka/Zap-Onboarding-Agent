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
