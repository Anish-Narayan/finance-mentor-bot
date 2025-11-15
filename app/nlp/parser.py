import re
from typing import Dict, Any, Optional

INTENT_KEYWORDS = {
    'expense': ['spent', 'paid', 'bought', 'expense', 'cost', 'purchase'],
    'income': ['received', 'got', 'earned', 'income', 'added', 'credited'],
    'summary': ['summary', 'report', 'how much', 'show expenses', 'show income'],
    'balance': ['balance', 'remaining', 'how much money left'],
    'help': ['/help', 'help'],
    'start': ['/start']
}

STOP_WORDS = {'on', 'for', 'at', 'a', 'the', 'my', 'i', 'in', 'of', 'was', 'is'}

# FIXED: handles "1000000", "1,000,000", "₹1000000", "₹ 1,000,000.50"
AMOUNT_REGEX = r'₹?\s?((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?)'


def get_intent(text: str) -> str:
    text_lower = text.lower()

    # Ranked keyword scanning
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return intent

    # If there is a number, default to expense
    if re.search(AMOUNT_REGEX, text_lower):
        return 'expense'

    return 'unknown'


def parse_transaction_message(text: str) -> Optional[Dict[str, Any]]:
    """Extracts type (income/expense), amount, category, description."""
    text_lower = text.lower()

    # Determine transaction type
    txn_type = 'income' if any(k in text_lower for k in INTENT_KEYWORDS['income']) else 'expense'

    # Extract amount
    match = re.search(AMOUNT_REGEX, text_lower)
    if not match:
        return None

    raw_amount = match.group(1)
    amount = float(raw_amount.replace(',', ''))

    # Remove the matched amount token (match.group(0) includes currency symbol)
    category_text = text_lower.replace(match.group(0), '')

    # Remove intent-related keywords
    for kw_list in INTENT_KEYWORDS.values():
        for kw in kw_list:
            category_text = category_text.replace(kw, '')

    # Clean stopwords (token-based)
    tokens = [t for t in category_text.split() if t not in STOP_WORDS]
    category = " ".join(tokens).strip()

    if not category:
        category = "general"

    return {
        'type': txn_type,
        'amount': amount,
        'category': category,
        'description': text
    }
