from api.v1.habr.habr import router as habr_router
from api.v1.telegram.telegram import router as telegram_router
from fastapi import APIRouter


__all__ = ["router"]


router = APIRouter()
router.include_router(telegram_router, prefix="/telegram")
router.include_router(habr_router, prefix="/habr")
