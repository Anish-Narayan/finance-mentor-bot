# app/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.users import get_all_user_ids
from app.services.finance_service import generate_weekly_summary
from app.bot_setup import bot

scheduler = AsyncIOScheduler(timezone="UTC")

async def send_weekly_summaries():
    """Job to send a weekly summary to all users."""
    print("Scheduler running: Sending weekly summaries...")
    try:
        user_ids = get_all_user_ids()
        for user_id in user_ids:
            try:
                summary_message = await generate_weekly_summary(int(user_id))
                await bot.send_message(
                    chat_id=user_id, 
                    text=summary_message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"Failed to send summary to user {user_id}: {e}")
    except Exception as e:
        print(f"Error fetching user IDs for scheduler: {e}")

def start_scheduler():
    # Schedule to run every Sunday at 14:00 UTC (e.g., 7:30 PM IST)
    scheduler.add_job(send_weekly_summaries, 'cron', day_of_week='sun', hour=14, minute=0)
    scheduler.start()
    print("Scheduler started. Weekly summaries will be sent on Sundays at 14:00 UTC.")