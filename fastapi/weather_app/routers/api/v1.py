"""
Router configuration for v1 REST API of the application.
"""

from weather_app.routers.api import weather

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")
router.include_router(weather.router)
