from typing import Annotated

from api.v1.telegram.schemas import TelegramChannelMessagesResponse
from clients import telegram_client
from common.logger import get_logger
from fastapi import APIRouter, HTTPException, Query


__all__ = ["router"]

logger = get_logger(__name__)

router = APIRouter(prefix="/telegram")


@router.get("/channel/{channel_username}/messages")
async def channel_messages(
    channel_username: str, after_message_id: Annotated[int | None, Query()] = None
) -> TelegramChannelMessagesResponse:
    newest_message_id = await telegram_client.get_newest_message_id(channel_username)
    if not newest_message_id:
        return TelegramChannelMessagesResponse(messages=[])

    if after_message_id is None:
        # Парсим offset_last_message последних сообщений для актуализации вакансий
        offset_last_message = 100
        after_message_id = max(1, newest_message_id - offset_last_message)
        logger.debug("Last message id is unknown, using %s", after_message_id)

    max_messages_interval = 300
    if (newest_message_id - after_message_id) > max_messages_interval:
        msg = f"Messages interval great then {max_messages_interval}. Increase after_message_id if possible"
        raise HTTPException(status_code=500, detail=msg)

    # +1 т.к. не нужно парсить уже известное сообщение и идем включительно до последнего сообщения
    message_ids_to_parse = list(range(after_message_id + 1, newest_message_id + 1))
    messages = await telegram_client.get_detailed_messages_by_message_ids(channel_username, message_ids_to_parse)

    return TelegramChannelMessagesResponse(messages=messages)
