from typing import TYPE_CHECKING, Annotated

from api.v1.telegram.schemas import TelegramChannelMessagesResponse, TelegramVacanciesQuery
from clients import telegram_client
from fastapi import APIRouter, Query


if TYPE_CHECKING:
    from schemas import TelegramChannelMessageSchema

__all__ = ["router"]


router = APIRouter()


@router.get("/messages")
async def channel_messages(query: Annotated[TelegramVacanciesQuery, Query()]) -> TelegramChannelMessagesResponse:
    newest_message_id = await telegram_client.get_newest_message_id(query.channel_username)
    if not newest_message_id:
        return TelegramChannelMessagesResponse(messages=[])

    messages: list[TelegramChannelMessageSchema] = []
    current_id = newest_message_id

    while current_id > 0:
        message = await telegram_client.get_detailed_message(query.channel_username, current_id)
        if message is None:
            current_id -= 1
            continue

        # Если сообщение старее, чем date_gte
        if message.datetime < query.date_gte:
            break

        messages.append(message)
        current_id -= 1

    return TelegramChannelMessagesResponse(messages=messages)
