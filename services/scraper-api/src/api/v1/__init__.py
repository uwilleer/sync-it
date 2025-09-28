from api.v1.telegram import router as telegram_router
from fastapi import APIRouter


__all__ = ["router"]


router = APIRouter()
router.include_router(telegram_router)
