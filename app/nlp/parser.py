# app/nlp/parser.py
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

AMOUNT_REGEX = r'₹?\s?(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d+(\.\d{1,2})?)'


def get_intent(text: str) -> str:
    text_lower = text.lower()

    # Ranked keyword scanning
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return intent

    # If there is a number, default to expense (transaction)
    if re.search(AMOUNT_REGEX, text):
        return 'expense'

    return 'unknown'


def parse_transaction_message(text: str) -> Optional[Dict[str, Any]]:
    """Extracts type (income/expense), amount, category, description."""
    text_lower = text.lower()

    # Determine transaction type
    if any(k in text_lower for k in INTENT_KEYWORDS['income']):
        txn_type = 'income'
    else:
        txn_type = 'expense'

    # Extract amount (supports ₹, commas, decimals)
    match = re.search(AMOUNT_REGEX, text)
    if not match:
        return None

    raw_amount = match.group(1).replace(',', '')
    amount = float(raw_amount)

    # Extract category
    category_text = text_lower.replace(raw_amount, '')

    for keyword_list in INTENT_KEYWORDS.values():
        for k in keyword_list:
            category_text = category_text.replace(k, '')

    for sw in STOP_WORDS:
        category_text = category_text.replace(f' {sw} ', ' ')

    category = category_text.strip(' .₹').strip()
    if not category:
        category = "general"

    return {
        'type': txn_type,
        'amount': amount,
        'category': category,
        'description': text
    }
