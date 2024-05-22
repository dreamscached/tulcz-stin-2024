"""
Router configuration for /weather API route group + route handlers.
"""

from typing import Annotated

from weather_app.errors import UpstreamError
from weather_app.services.weather import WeatherService, get_weather_service

from fastapi import APIRouter, Depends, HTTPException, Path, status

router = APIRouter(prefix="/weather")

@router.get(
    path="/forecast/{toponym}",
    summary="Get forecast",
    description="Get a weather forecast for the given toponym"
)
async def get_forecast(
    toponym: Annotated[str | None, Path(
        title="Toponym to lookup", example="Liberec, CZ",
        min_length=2, max_length=32
    )],
    weather_service: WeatherService = Depends(get_weather_service)
) -> dict:
    """
    Locate a toponym and return possible matches with geographical coordinates.
    """

    try:
        results = await weather_service.get_query_toponym(toponym)
    except UpstreamError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch data from upstream API."
        ) from e

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Toponym was not found."
        )

    top_data = results[0]
    top_location = (top_data.latitude, top_data.longitude)

    forecast = await weather_service.get_weather_forecast(top_location)
    return {"forecast": forecast}
