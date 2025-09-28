from api import health
from fastapi import APIRouter


__all__ = ["router"]


router = APIRouter()

router.include_router(health.router, prefix="/health")
