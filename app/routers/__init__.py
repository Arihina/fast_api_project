from fastapi import APIRouter

from .descriptions import router as descriptions_router
from .orders import router as orders_router
from .buyers import router as buyer_router
from .providers import router as provider_router

router = APIRouter()

router.include_router(descriptions_router)
router.include_router(orders_router)
router.include_router(buyer_router)
router.include_router(provider_router)
