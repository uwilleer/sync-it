import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
import uvloop


load_dotenv("../infra/.env")

phone = os.getenv("TELETHON_PHONE")
password = os.getenv("TELETHON_PASSWORD")
api_id = int(os.getenv("SCRAPER_API_TELETHON_API_ID"))
api_hash = os.getenv("SCRAPER_API_TELETHON_API_HASH")

assert all((phone, password, api_id, api_hash))


async def main() -> None:
    async with TelegramClient(StringSession(), api_id, api_hash) as client:
        await client.start(phone=phone, password=password)
        session_string = client.session.save()

        raise Exception(f"SCRAPER_API_TELETHON_SESSION_STRING={session_string}")  # noqa: TRY002


if __name__ == "__main__":
    uvloop.run(main())
