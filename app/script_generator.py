import json
import re
from typing import Any

try:
    from langchain_core.prompts import PromptTemplate
except ImportError:  # pragma: no cover
    PromptTemplate = None

try:
    from langchain_groq import ChatGroq
except ImportError:  # pragma: no cover
    ChatGroq = None


def generate_onboarding_script(customer_card: dict[str, Any]) -> str:
    """Generate a Hebrew onboarding phone-call script from a customer card."""
    if PromptTemplate is None or ChatGroq is None:
        raise ImportError("Missing LangChain/Groq dependencies for script generation")

    prompt = PromptTemplate(
        input_variables=["customer_card"],
        template=(
            "אתה יועץ מכירות ושירות לקוחות מנוסה של Zap / דפי זהב.\n"
            "כתוב תסריט שיחת אונבורדינג טלפונית חמה ומקצועית עבור נציג Zap.\n"
            "השתמש בנתוני כרטיס הלקוח הבאים:\n"
            "{customer_card}\n\n"
            "דרישות קשיחות לתסריט:\n"
            "1. פתיח אישי - שימוש בשם הבעלים ובשם העסק אם קיימים.\n"
            "2. אישור פרטים קיימים - אימות תמציתי של הנתונים שנאספו.\n"
            "3. הצגת ערך - הסבר מה Zap/דפי זהב יכולים להציע לסוג העסק הזה.\n"
            "4. שאלות גילוי צרכים - בדיוק 3 שאלות פתוחות.\n"
            "5. סגירה וצעד הבא - סיכום קצר והצעת המשך ברורה.\n\n"
            "הנחיות סגנון:\n"
            "- כתיבה בעברית טבעית, נעימה ומקצועית.\n"
            "- פורמט ברור עם כותרת לכל סעיף.\n"
            "- ללא תוספות שלא נדרשו.\n"
        ),
    )

    llm = ChatGroq(model="qwen/qwen3-32b")
    chain = prompt | llm
    response = chain.invoke(
        {"customer_card": json.dumps(customer_card, ensure_ascii=False, indent=2)}
    )
    raw_text = response.content if isinstance(response.content, str) else str(response.content)
    business_name = customer_card.get("business_name") or "העסק שלך"
    return _sanitize_hebrew_script(raw_text, str(business_name))


def _sanitize_hebrew_script(script: str, business_name: str) -> str:
    title = f"**תסריט שיחת אונבורדינג - {business_name}**"
    section_titles = {
        "פתיחה אישית",
        "אימות פרטים קיימים",
        "הצגת ערך",
        "שאלות גילוי צרכים",
        "סיכום וצעד הבא",
        "הצעות צעד הבא:",
    }

    lines = [line.strip() for line in script.splitlines() if line.strip()]
    filtered: list[str] = []

    for line in lines:
        if line.startswith("```"):
            continue
        if line.startswith(("First,", "Wait,", "But ", "I need ", "The user ")):
            continue
        if "רוצה להתחיל" in line:
            continue
        normalized_line = line.replace("#", "").strip()
        normalized_line = _remove_non_hebrew_text(normalized_line)
        if not normalized_line:
            continue
        is_section_title = normalized_line.strip("* ").strip() in section_titles
        has_hebrew = re.search(r"[\u0590-\u05FF]", normalized_line) is not None
        is_list_item = normalized_line.startswith("-") or re.match(r"^\d+\.", normalized_line)
        if has_hebrew or is_section_title or is_list_item:
            filtered.append(normalized_line)

    start_idx = next(
        (idx for idx, line in enumerate(filtered) if "תסריט שיחת אונבורדינג" in line),
        0,
    )
    normalized = filtered[start_idx:] if filtered else []

    if not normalized or "תסריט שיחת אונבורדינג" not in normalized[0]:
        normalized = [title, *normalized]
    else:
        normalized[0] = title

    for idx, line in enumerate(normalized):
        plain = line.strip("* ").strip()
        if plain in section_titles:
            normalized[idx] = f"**{plain}**"

    summary_idx = next(
        (idx for idx, line in enumerate(normalized) if "סיכום וצעד הבא" in line),
        -1,
    )
    if summary_idx != -1:
        normalized = normalized[: summary_idx + 1]
        normalized[-1] = "**סיכום וצעד הבא**"

    return "\n".join(normalized).strip()


def _remove_non_hebrew_text(line: str) -> str:
    return "".join(
        ch
        for ch in line
        if (
            "\u0590" <= ch <= "\u05FF"
            or ch.isdigit()
            or ch in " .,:;!?-–—\"'()[]*/+_%"
            or ch == "*"
        )
    ).strip()
