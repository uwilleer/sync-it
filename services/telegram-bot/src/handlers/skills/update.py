from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from callbacks.skill import SkillActionEnum, SkillCallback
from commands import BotCommandEnum
from handlers.skills.helpers import update_skills


router = Router()


@router.message(Command(BotCommandEnum.UPDATE_SKILLS))
async def handle_update_skills_command(message: Message, state: FSMContext) -> None:
    await update_skills(message, state)


@router.callback_query(SkillCallback.filter(F.action == SkillActionEnum.UPDATE_SKILLS))
async def handle_update_skills_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await update_skills(callback, state)
