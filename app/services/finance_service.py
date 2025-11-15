# app/services/finance_service.py
from app.db import transactions as txn_db
from app.db import budgets as budget_db
from app.db import goals as goal_db
from datetime import datetime, timedelta

async def process_expense(user_id: int, text: str) -> str:
    """
    Parse a message like 'spent 100 on snacks' and log the expense.
    """
    try:
        # Basic parsing logic (replace with your NLP parser if available)
        words = text.lower().split()
        amount = float(next(word for word in words if word.replace('.', '', 1).isdigit()))
        category = words[words.index("on") + 1] if "on" in words else "misc"
        description = " ".join(words[words.index("on") + 1:]) if "on" in words else category
        txn_type = "expense"

        # Add transaction
        txn_db.add_transaction(user_id, amount, category, description, txn_type)

        # Update goals if the category is linked to a goal
        all_goals = goal_db.get_all_goals(user_id)
        for goal in all_goals:
            if goal['goal_name'].lower() == category:
                goal_db.update_goal_progress(user_id, category, amount)

        # Check budget
        budget = budget_db.get_budget(user_id, category)
        response = f"Logged {amount} in {category}."
        if budget:
            # Calculate total spent in category in last 30 days
            txns = await txn_db.get_transactions_for_period(user_id, days=30)
            spent = sum(t['amount'] for t in txns if t['category'] == category.lower())
            if spent > budget['amount']:
                response += f" ⚠️ You've exceeded your {category} budget of {budget['amount']}!"

        return response

    except Exception as e:
        return f"Failed to log expense: {e}"

def get_start_message() -> str:
    return (
        "Welcome to Finance Mentor Bot! 💰\n\n"
        "You can log expenses like 'spent 100 on snacks', "
        "check your weekly summary with 'summary', or set budgets and goals."
    )

def get_help_message() -> str:
    return (
        "Here’s what I can do:\n"
        "- Log an expense: 'spent 50 on groceries'\n"
        "- Show weekly summary: 'summary'\n"
        "- Set a budget: 'set budget 200 for groceries'\n"
        "- Set a goal: 'set goal vacation 500'\n"
        "- Check your budgets or goals anytime!"
    )

async def generate_weekly_summary(user_id: int) -> str:
    """
    Generate a weekly summary for a user, showing total expenses by category.
    """
    try:
        txns = await txn_db.get_transactions_for_period(user_id, days=7)
        if not txns:
            return "No transactions in the past week."

        summary = {}
        for t in txns:
            category = t['category']
            summary[category] = summary.get(category, 0) + t['amount']

        summary_lines = [f"{cat}: {amt:.2f}" for cat, amt in summary.items()]
        return "📊 Weekly Summary:\n" + "\n".join(summary_lines)

    except Exception as e:
        return f"Error generating summary: {e}"
async def get_balance(user_id: int) -> str:
    """
    Get the current balance (income - expenses) for the user.
    """
    try:
        balance = await txn_db.get_balance(user_id)
        return f"Your current balance is: ₹{balance:.2f}"
    except Exception as e:
        return f"Error fetching balance: {e}"
async def process_transaction(user_id: int, text: str) -> str:
    """
    Process a transaction message, determining if it's income or expense.
    """
    from app.nlp.parser import parse_transaction_message

    parsed = parse_transaction_message(text)
    if not parsed:
        return "Could not parse the transaction. Please ensure you include an amount."

    amount = parsed['amount']
    category = parsed.get('category', 'misc')
    description = parsed.get('description', category)
    txn_type = parsed['type']

    try:
        txn_db.add_transaction(user_id, amount, category, description, txn_type)

        return f"Logged {txn_type} of ₹{amount:.2f} in category '{category}'."

    except Exception as e:
        return f"Failed to log transaction: {e}"
