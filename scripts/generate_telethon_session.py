import os
import shlex

import asyncssh
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
import uvloop


load_dotenv("../infra/.env")

phone = os.getenv("TELETHON_PHONE")
password = os.getenv("TELETHON_PASSWORD")
api_id = int(os.getenv("SCRAPER_API_TELETHON_API_ID"))
api_hash = os.getenv("SCRAPER_API_TELETHON_API_HASH")

SSH_HOST = os.getenv("SSH_HOST")
SSH_USER = os.getenv("SSH_USER")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")
REMOTE_ENV_PATH = os.getenv("REMOTE_ENV_PATH")
ENV_NAME = "SCRAPER_API_TELETHON_SESSION_STRING"

assert all((phone, password, api_id, api_hash, SSH_HOST, SSH_USER, SSH_PASSWORD, REMOTE_ENV_PATH))


async def update_env_on_server(session_string: str) -> None:
    async with asyncssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, known_hosts=None) as conn:
        result = await conn.run(f"cat {REMOTE_ENV_PATH}", check=True)
        env_content = str(result.stdout)

        new_line = f"{ENV_NAME}={session_string}"
        lines = env_content.split("\n")
        replaced = False

        for i, line in enumerate(lines):
            if line.startswith(f"{ENV_NAME}="):
                lines[i] = new_line
                replaced = True
                break

        if not replaced:
            lines.append(new_line)

        escaped_env = shlex.quote("\n".join(lines))
        await conn.run(f"printf %s {escaped_env} > {REMOTE_ENV_PATH}", check=True)


async def main() -> None:
    async with TelegramClient(StringSession(), api_id, api_hash) as client:
        await client.start(phone=phone, password=password)
        session_string = client.session.save()

    await update_env_on_server(session_string)
    print(f"{ENV_NAME} обновлён на {SSH_HOST}:{REMOTE_ENV_PATH}")  # noqa: T201


if __name__ == "__main__":
    uvloop.run(main())
