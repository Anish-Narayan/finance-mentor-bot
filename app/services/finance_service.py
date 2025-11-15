from app.db import transactions as txn_db
from app.db import budgets as budget_db
from app.db import goals as goal_db
from datetime import datetime, timedelta

async def process_transaction(user_id: int, text: str) -> str:
    """
    Process a transaction message (income or expense) using the NLP parser.
    """
    from app.nlp.parser import parse_transaction_message

    parsed = parse_transaction_message(text)  # no txn_type argument
    if not parsed:
        return "Could not parse the transaction. Please include an amount."

    amount = parsed['amount']
    category = parsed.get('category', 'general')
    description = parsed.get('description', category)
    txn_type = parsed['type']

    try:
        # Add transaction to DB
        txn_db.add_transaction(user_id, amount, category, description, txn_type)

        # Update goals if expense
        if txn_type == 'expense':
            all_goals = goal_db.get_all_goals(user_id)
            for goal in all_goals:
                if goal['goal_name'].lower() == category:
                    goal_db.update_goal_progress(user_id, category, amount)

            # Check budget
            budget = budget_db.get_budget(user_id, category)
            response = f"Logged {amount} in {category}."
            if budget:
                txns = await txn_db.get_transactions_for_period(user_id, days=30)
                spent = sum(t['amount'] for t in txns if t['category'] == category.lower())
                if spent > budget['amount']:
                    response += f" ⚠️ You've exceeded your {category} budget of {budget['amount']}!"
            else:
                response = f"Logged {txn_type} of ₹{amount:.2f} in category '{category}'."

        else:
            response = f"Logged {txn_type} of ₹{amount:.2f} in category '{category}'."

        return response

    except Exception as e:
        return f"Failed to log transaction: {e}"


def get_start_message() -> str:
    return (
        "Welcome to Finance Mentor Bot by Anish! 💰\n\n"
        "You can log expenses like 'spent 100 on snacks', "
        "check your weekly summary with 'summary', or set budgets and goals.,"
        "Check my GitHub for more info: https://github.com/Anish-Narayan and feel free to contribute! 🚀"
        "Message me in linkedIn: https://www.linkedin.com/in/s-anish-narayan/ for any collaborations!"
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


# app/services/finance_service.py
from app.db import transactions as txn_db
from datetime import datetime, timedelta
from collections import defaultdict

async def generate_weekly_summary(user_id: int) -> str:
    """
    Generate a weekly summary for a user, showing income, expenses, net balance, and expense breakdown.
    """
    try:
        txns = await txn_db.get_transactions_for_period(user_id, days=7)
        if not txns:
            return "No transactions in the past week."

        total_income = 0.0
        total_expense = 0.0
        expense_breakdown = defaultdict(float)

        for t in txns:
            amount = t['amount']
            category = t.get('category', 'general').title()
            if t['type'] == 'income':
                total_income += amount
            else:
                total_expense += amount
                expense_breakdown[category] += amount

        net = total_income - total_expense

        # Build summary message
        summary_lines = [
            "📊 Weekly Finance Summary\n",
            f"Income: ₹{total_income:.2f}",
            f"Expenses: ₹{total_expense:.2f}",
            "-------------------------",
        ]

        net_line = f"💵 Net: ₹{net:.2f}"
        if net < 0:
            net_line += " ⚠️ You spent more than you earned!"
        summary_lines.append(net_line)

        if expense_breakdown:
            summary_lines.append("\nExpense Breakdown:")
            for category, amt in expense_breakdown.items():
                summary_lines.append(f"• {category}: ₹{amt:.2f}")

        summary_lines.append("\n✨ Tip: Keep an eye on your top expense category!")

        return "\n".join(summary_lines)

    except Exception as e:
        return f"Error generating summary: {e}"


async def get_balance(user_id: int) -> str:
    try:
        balance = await txn_db.get_balance(user_id)
        return f"Your current balance is: ₹{balance:.2f}"
    except Exception as e:
        return f"Error fetching balance: {e}"
