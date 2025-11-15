# app/main.py
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.telegram_webhook import router as telegram_router
from app.bot_setup import set_telegram_webhook, clear_telegram_webhook
from app.core.scheduler import start_scheduler, scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on application startup
    print("Starting up...")
    await set_telegram_webhook()
    start_scheduler()
    yield
    # Runs on application shutdown
    print("Shutting down...")
    await clear_telegram_webhook()
    scheduler.shutdown()

app = FastAPI(
    title="AI Personal Finance Mentor Bot",
    description="A Telegram bot to help students manage their finances.",
    lifespan=lifespan
)

app.include_router(telegram_router, prefix="/api")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Finance Mentor Bot is running!"}

if __name__ == "__main__":
    # For local development
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)