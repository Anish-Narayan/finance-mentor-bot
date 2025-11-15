# app/bot_setup.py
from telegram.ext import Application
from app.core.config import settings

# Initialize the bot application
application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
bot = application.bot

async def set_telegram_webhook():
    """Sets the Telegram webhook on application startup."""
    webhook_url = f"{settings.WEBHOOK_URL}/api/telegram"
    if not webhook_url.startswith("https://"):
        print("WARNING: WEBHOOK_URL must be HTTPS.")
        return
    await bot.set_webhook(url=webhook_url)
    print(f"Telegram webhook has been set to {webhook_url}")

async def clear_telegram_webhook():
    """Clears the Telegram webhook on application shutdown."""
    await bot.delete_webhook()
    print("Telegram webhook has been cleared.")