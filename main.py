import asyncio
import logging

from telegram.ext import Application

from config import BOT_TOKEN, CHANNEL_ID, PRICE_INTERVAL
from price_service import get_all_prices


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def format_price(price):
    return f"{price:,}"


async def send_price_report(application):
    try:
        prices = await get_all_prices()

        dollar = prices["dollar"]
        gold = prices["melted_gold"]

        message = (
            "📊 قیمت لحظه‌ای بازار آزاد\n"
            "━━━━━━━━━━━━━━\n"
            f"💵 دلار آزاد: {format_price(dollar)} تومان\n"
            f"🟡طلای آب‌شده هر مثقال: {format_price(gold)} تومان\n"
            "━━━━━━━━━━━━━━"
        )

        await application.bot.send_message(
            chat_id=CHANNEL_ID,
            text=message
        )

        logger.info("گزارش قیمت با موفقیت ارسال شد.")

    except Exception:
        logger.exception("خطا در دریافت یا ارسال قیمت")


async def price_loop(application):
    while True:
        await send_price_report(application)
        await asyncio.sleep(PRICE_INTERVAL)


async def post_init(application):
    application.bot_data["price_task"] = asyncio.create_task(
        price_loop(application)
    )


async def post_shutdown(application):
    task = application.bot_data.get("price_task")

    if task:
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass


def main():
    if not BOT_TOKEN:
        raise ValueError("توکن ربات در متغیر BOT_TOKEN تنظیم نشده است.")

    if not CHANNEL_ID:
        raise ValueError("شناسه کانال در متغیر CHANNEL_ID تنظیم نشده است.")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    logger.info("ربات در حال راه‌اندازی است...")

    application.run_polling()


if __name__ == "__main__":
    main()
