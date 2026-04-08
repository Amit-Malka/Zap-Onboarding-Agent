import json
from typing import Any

from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq


def generate_onboarding_script(customer_card: dict[str, Any]) -> str:
    """Generate a Hebrew onboarding phone-call script from a customer card."""
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
    return response.content if isinstance(response.content, str) else str(response.content)
