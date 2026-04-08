from app.script_generator import _sanitize_hebrew_script


def test_sanitize_hebrew_script_removes_english_and_meta_text() -> None:
    raw_script = """
First, the script must have an introduction.
Wait, maybe mention Zap.
**תסריט שיחת אונבורדינג - פואד מיזוג אוויר**
**פתיחה אישית**
שלום וברכה.
This should not appear.
**סיכום וצעד הבא**
רוצה להתחיל?
"""
    cleaned = _sanitize_hebrew_script(raw_script, "פואד מיזוג אוויר")

    assert "First, the script" not in cleaned
    assert "Wait, maybe" not in cleaned
    assert "This should not appear." not in cleaned
    assert "רוצה להתחיל?" not in cleaned
    assert cleaned.startswith("**תסריט שיחת אונבורדינג - פואד מיזוג אוויר**")
    assert cleaned.rstrip().endswith("**סיכום וצעד הבא**")
    assert cleaned.splitlines()[-1] != "רוצה להתחיל?"


def test_sanitize_hebrew_script_adds_required_title_when_missing() -> None:
    raw_script = """
**פתיחה אישית**
שלום וברכה.
**סיכום וצעד הבא**
"""
    cleaned = _sanitize_hebrew_script(raw_script, "עסק לדוגמה")

    assert cleaned.startswith("**תסריט שיחת אונבורדינג - עסק לדוגמה**")
    assert "**סיכום וצעד הבא**" in cleaned


def test_sanitize_hebrew_script_removes_non_hebrew_foreign_chars() -> None:
    raw_script = """
**תסריט שיחת אונבורדינג - עסק לדוגמה**
**שאלות גילוי צרכים**
1. אילו תקניות אתם תוארו עליכם להשתפר ב客户服务 או תהליך השירות?
2. איך אתם נוהגים להנהל קשר עם לקוחות שדורשים שירות דחוף?
"""
    cleaned = _sanitize_hebrew_script(raw_script, "עסק לדוגמה")

    assert "客户服务" not in cleaned
