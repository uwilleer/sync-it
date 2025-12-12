from pydantic import HttpUrl


class TelegramChannelUrl(HttpUrl):
    """Custom URL for Telegram channel:
    Accepts 'username' or 'username/topic_id' as input.
    Internally stored as: https://t.me/s/<username>/<topic_id?>
    """

    def __init__(self, username: str) -> None:
        self._username, self._topic_id = self._parse_username(username)

        url = f"https://t.me/s/{self._username}"
        if self._topic_id:
            url += f"/{self._topic_id}"

        super().__init__(url)

    @property
    def channel_username(self) -> str:
        return self._username

    @property
    def channel_topic_id(self) -> int | None:
        return self._topic_id or None

    @staticmethod
    def _parse_username(value: str) -> tuple[str, int | None]:
        parts = value.split("/")

        if len(parts) == 1:
            return parts[0], None
        if len(parts) == 2:  # noqa: PLR2004
            return parts[0], int(parts[1])

        raise ValueError("Unexpected username format")
