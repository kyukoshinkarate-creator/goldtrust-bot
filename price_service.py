import aiohttp
import re
from bs4 import BeautifulSoup


BASE_URL = "https://www.tgju.org/profile/"

DOLLAR_URL = BASE_URL + "price_dollar_rl"
MELTED_GOLD_URL = BASE_URL + "gold_futures"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    )
}


def extract_current_price(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    # پیدا کردن عدد کنار عبارت «نرخ فعلی»
    patterns = [
        r"نرخ\s*فعلی\s*[:：]*\s*([\d,٬]+)",
        r"قیمت\s*فعلی\s*[:：]*\s*([\d,٬]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            value = re.sub(r"[^\d]", "", match.group(1))

            if value:
                return int(value)

    raise ValueError("قیمت در صفحه پیدا نشد")


async def fetch_price(session, url):
    async with session.get(
        url,
        headers=HEADERS,
        timeout=aiohttp.ClientTimeout(total=20)
    ) as response:
        response.raise_for_status()
        html = await response.text()

    return extract_current_price(html)


async def get_dollar_price():
    async with aiohttp.ClientSession() as session:
        price_rial = await fetch_price(session, DOLLAR_URL)

    # تبدیل ریال به تومان
    return round(price_rial / 10)


async def get_melted_gold_price():
    async with aiohttp.ClientSession() as session:
        price_rial_per_mesghal = await fetch_price(
            session,
            MELTED_GOLD_URL
        )

    # تبدیل ریال به تومان (قیمت مثقال)
    price_toman_per_mesghal = price_rial_per_mesghal / 10

    return round(price_toman_per_mesghal)


async def get_all_prices():
    dollar, gold = await __import__("asyncio").gather(
        get_dollar_price(),
        get_melted_gold_price()
    )

    return {
        "dollar": dollar,
        "melted_gold": gold
          }
