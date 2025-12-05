from aiogram import Router
from callbacks.skill import SkillCallback
from handlers.skills.process import router as process_router
from handlers.skills.toggle import router as toggle_router
from handlers.skills.update import router as update_router


router = Router(name=SkillCallback.__prefix__)
router.include_routers(
    process_router,
    toggle_router,
    update_router,
)

__all__ = ["router"]
