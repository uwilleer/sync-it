import asyncio
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, cast

from aiogram.enums import ParseMode
from celery_app import app
from clients import skill_client
from common.logger import get_logger
from core import service_config
from core.loader import bot
from database.models.enums import PreferencesCategoryCodeEnum
from keyboard.inline.main import main_menu_keyboard
from keyboard.inline.skills import process_update_skills_keyboard
from schemas.user_preference import UserPreferenceCreate
from tasks.schemas import FileResumePayloadSchema, TextResumePayloadSchema
from unitofwork import UnitOfWork
from utils.text_extractor import TextExtractor

from services import UserPreferenceService


if TYPE_CHECKING:
    from celery import Task


__all__ = ["process_resume"]


logger = get_logger(__name__)


@app.task(name="process_resume", bind=True, max_retries=3)
def process_resume(
    self: "Task[Any, Any]", user_id: int, chat_id: int, data: dict[str, Any], *, toggle: bool = False
) -> None:
    loop = asyncio.get_event_loop()

    data_type = data.get("type")

    try:
        if data_type == "text":
            text_schema = TextResumePayloadSchema(**data)
            text = text_schema.text
        elif data_type == "file":
            file_schema = FileResumePayloadSchema(**data)
            with NamedTemporaryFile(suffix=file_schema.suffix) as tmp:
                loop.run_until_complete(bot.download_file(file_schema.file_path, destination=tmp.name))
                extractor = TextExtractor()
                text = extractor.read(tmp.name)
        else:
            raise ValueError(f"Invalid data type: {data_type}")  # noqa: TRY301

        loop.run_until_complete(_extract_and_save_user_preferences(user_id, text, chat_id, toggle=toggle))
    except Exception as e:
        logger.exception("Error processing resume", exc_info=e)

        if self.request.retries != self.max_retries:
            loop.run_until_complete(
                bot.send_message(
                    chat_id,
                    "⚠️ Произошла ошибка при извлечении навыков.\n"
                    f"Пробуем еще раз. Попытка {self.request.retries + 1}/{self.max_retries}",
                )
            )

        if self.request.retries >= cast("int", self.max_retries):
            loop.run_until_complete(
                bot.send_message(
                    chat_id,
                    "⚠️ Произошла ошибка при извлечении навыков.\nПроверьте корректность содержимого файла.\n\n"
                    f"Если вы считаете, что ошибка на нашей стороне, пожалуйста, обратитесь в поддержку: "
                    f"@{service_config.support_username}",
                    reply_markup=main_menu_keyboard(),
                )
            )
        else:
            raise self.retry(countdown=60, exc=e) from e


async def _extract_and_save_user_preferences(user_id: int, text: str, chat_id: int, *, toggle: bool = False) -> None:
    skills = await skill_client.extract_skills_from_text(text)
    if not skills:
        await bot.send_message(
            chat_id,
            "⚠️ В приведенном тексте не найдено ни одного навыка.\n\n"
            f"Если вы считаете, что это ошибка и ваш навык существует, пожалуйста, обратитесь в поддержку: "
            f"@{service_config.support_username}",
            reply_markup=main_menu_keyboard(),
        )
        return

    async with UnitOfWork() as uow:
        service = UserPreferenceService(uow)

        if toggle:
            added: list[str] = []
            removed: list[str] = []
            for s in skills:
                pref = UserPreferenceCreate(
                    user_id=user_id,
                    category_code=PreferencesCategoryCodeEnum.SKILL,
                    item_id=s.id,
                    item_name=s.name,
                )
                is_added = await service.toggle_preference(pref)
                if is_added:
                    added.append(s.name)
                else:
                    removed.append(s.name)

            await uow.commit()

            msg_parts = []
            if added:
                msg_parts.append(
                    "✅ Добавлены навыки:\n"
                    + ", ".join(f"<code>{s}</code>" for s in sorted(added, key=lambda n: n.casefold()))
                )
            if removed:
                msg_parts.append(
                    "❌ Удалены навыки:\n"
                    + ", ".join(f"<code>{s}</code>" for s in sorted(removed, key=lambda n: n.casefold()))
                )

            user_skills = await service.get_by_user_id(user_id)
            user_skills_str = ", ".join(
                f"<code>{s.item_name}</code>" for s in sorted(user_skills, key=lambda n: n.item_name.casefold())
            )
            changed_skills_str = "\n\n".join(msg_parts)

            await bot.send_message(
                chat_id,
                f"Ваши актуальные навыки:\n{user_skills_str}\n\n{changed_skills_str}\n\n"
                f"Если вы считаете, что какой-то навык не распознался, пожалуйста, обратитесь в поддержку: "
                f"@{service_config.support_username}",
                reply_markup=process_update_skills_keyboard(),
                parse_mode=ParseMode.HTML,
            )
        else:
            added_preferences = await service.replace_user_preferences(
                user_id=user_id,
                category_code=PreferencesCategoryCodeEnum.SKILL,
                preferences=[
                    UserPreferenceCreate(
                        user_id=user_id,
                        category_code=PreferencesCategoryCodeEnum.SKILL,
                        item_id=s.id,
                        item_name=s.name,
                    )
                    for s in skills
                ],
            )
            await uow.commit()

            sorted_skills = sorted(added_preferences, key=lambda p: p.item_name.casefold())
            added_skills_str = ", ".join(f"<code>{s.item_name}</code>" for s in sorted_skills)

            await bot.send_message(
                chat_id,
                f"✅ Ваши навыки успешно обновлены.\n\n"
                f"Теперь вы будете получать вакансии, релевантные под ваши навыки:\n"
                f"{added_skills_str}",
                reply_markup=process_update_skills_keyboard(),
                parse_mode=ParseMode.HTML,
            )
