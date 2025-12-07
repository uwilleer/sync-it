import base64
import logging
import os
import pathlib

import aiofiles
import asyncssh
from dotenv import load_dotenv
from telethon import TelegramClient
import uvloop


load_dotenv("../infra/.env")

phone = os.getenv("TELETHON_PHONE")
password = os.getenv("TELETHON_PASSWORD")
session_name = os.getenv("SCRAPER_API_TELETHON_SESSION_NAME")
api_id = int(os.getenv("SCRAPER_API_TELETHON_API_ID"))
api_hash = os.getenv("SCRAPER_API_TELETHON_API_HASH")

SSH_HOST = os.getenv("SSH_HOST")
SSH_USER = os.getenv("SSH_USER")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")
REMOTE_ENV_PATH = os.getenv("REMOTE_ENV_PATH")
ENV_NAME = "SCRAPER_API_TELETHON_SESSION_BASE64"

assert all((phone, password, api_id, api_hash, SSH_HOST, SSH_USER, SSH_PASSWORD, REMOTE_ENV_PATH))


async def update_env_on_server(session_b64: str) -> None:
    async with asyncssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, known_hosts=None) as conn:
        result = await conn.run(f"cat {REMOTE_ENV_PATH}", check=True)
        env_content = result.stdout

        new_line = f'{ENV_NAME}="{session_b64}"'

        lines = env_content.split("\n")
        replaced = False

        for i, line in enumerate(lines):
            if line.startswith(ENV_NAME):
                lines[i] = new_line
                replaced = True
                break

        if not replaced:
            raise ValueError(f"Environment variable '{ENV_NAME}' not found.")

        updated_env = "\n".join(lines)

        await conn.run(f"cat <<EOF > {REMOTE_ENV_PATH}\n{updated_env}\nEOF", check=True)


async def main() -> None:
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start(phone=phone, password=password)

    async with aiofiles.open(pathlib.Path(f"{session_name}.session"), "rb") as f:
        session_bytes = await f.read()

    session_b64 = base64.b64encode(session_bytes).decode("utf-8")

    async with aiofiles.open(pathlib.Path("telethon.session.b64"), "w", encoding="utf-8") as f:
        await f.write(session_b64)

    await update_env_on_server(session_b64)


if __name__ == "__main__":
    uvloop.run(main())
