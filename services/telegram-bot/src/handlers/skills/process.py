from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from handlers.skills.helpers import parse_resume_input
from handlers.skills.schemas import ResumeError, ResumeTypeEnum
from schemas.user import UserRead
from states import PreferencesState
from tasks import process_resume


router = Router()


@router.message(StateFilter(PreferencesState.waiting_for_data, PreferencesState.waiting_toggle_skills))
async def handle_process_skills(message: Message, state: FSMContext, user: UserRead) -> None:
    need_toggle = await state.get_state() == PreferencesState.waiting_toggle_skills

    payload = await parse_resume_input(message)
    if isinstance(payload, ResumeError):
        await message.reply(payload.message, reply_markup=payload.reply_markup, parse_mode=payload.parse_mode)
        return

    file_type_text = "файла" if payload.type == ResumeTypeEnum.FILE else "текста"
    await message.answer(
        f"ℹ️ Начинаю извлечение навыков из {file_type_text}.\nПожалуйста, подождите, это может занять некоторое время.",
    )

    process_resume.delay(user.id, message.chat.id, payload.model_dump(), toggle=need_toggle)
    await state.clear()
