from fastapi import APIRouter, Request
from telegram import Update
from app.bot_setup import application
from app.db import users as db_users
from app.nlp import parser
from app.services import finance_service

router = APIRouter()

@router.post("/telegram")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram updates by processing them."""
    body = await request.json()
    update = Update.de_json(body, application.bot)
    
    # Skip if no message or no text
    if not update.message or not update.message.text:
        return {"status": "ok, no message to process"}

    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    text = update.message.text
    
    # Ensure the user exists in our DB
    db_users.get_or_create_user(user_id, username)
    
    # Determine the intent of the message
    intent = parser.get_intent(text)
    response_message = ""

    if intent == 'start':
        response_message = finance_service.get_start_message()

    elif intent == 'help':
        response_message = finance_service.get_help_message()

    elif intent in ('expense', 'income'):
        # Process either an expense or income
        response_message = await finance_service.process_transaction(user_id, text)

    elif intent == 'summary':
        response_message = await finance_service.generate_weekly_summary(user_id)

    elif intent == 'balance':
        response_message = await finance_service.get_balance(user_id)

    else:
        response_message = (
            "Sorry, I didn't understand that.\n\n"
            "Try logging an expense or income like:\n"
            "`spent 100 on snacks`\n"
            "`earned 500 from freelancing`\n\n"
            "Or ask for:\n"
            "`summary`, `balance`, `help`"
        )

    # Send the response back to the user
    await application.bot.send_message(
        chat_id=user_id, 
        text=response_message, 
        parse_mode='Markdown'
    )

    return {"status": "ok"}
