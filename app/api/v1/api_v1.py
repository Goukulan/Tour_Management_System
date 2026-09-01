from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.admin.destinations import router as destination_router
from app.api.v1.endpoints.admin.categories import router as categories_router
from app.api.v1.endpoints.admin.tours import router as admin_tours_router
from app.api.v1.endpoints.admin.departures import router as admin_departures_router
from app.api.v1.endpoints.admin.guides import router as guide_router
from app.api.v1.endpoints.admin.users import router as users_router
from app.api.v1.endpoints.destinations import router as public_destinations_router
from app.api.v1.endpoints.categories import router as public_categories_router
from app.api.v1.endpoints.tours import router as public_tours_router
from app.api.v1.endpoints.bookings import router as bookings
from app.api.v1.endpoints.admin.bookings import router as temporary_booking
from app.api.v1.endpoints.guide.departures import router as guide_departures_router
from app.api.v1.endpoints.payments import router as payments_router



router = APIRouter()

router.include_router(auth_router)
router.include_router(destination_router)
router.include_router(categories_router)
router.include_router(admin_tours_router)
router.include_router(admin_departures_router)
router.include_router(guide_router)
router.include_router(guide_departures_router)
router.include_router(users_router)
router.include_router(public_destinations_router)
router.include_router(public_categories_router)
router.include_router(public_tours_router)
router.include_router(bookings)
router.include_router(temporary_booking)
router.include_router(payments_router)
