from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from callbacks.noop import NoopActionEnum, NoopCallback
from keyboard.inline.main import main_menu_keyboard


router = Router(name=NoopCallback.__prefix__)


@router.callback_query(NoopCallback.filter(F.action == NoopActionEnum.DO_NOTHING))
async def handle_noop_callback(query: CallbackQuery) -> None:
    await query.answer("Ничего не произошло")


@router.message()
async def handle_noop_message(message: Message) -> None:
    await message.reply(
        "Я вас не понимаю 🥲",
        reply_markup=main_menu_keyboard(),
    )
