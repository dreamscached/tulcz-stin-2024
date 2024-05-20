"""
Router configuration for /weather API route group + route handlers.
"""

from weather_app.services.weather import WeatherService, get_weather_service

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/weather")

@router.get("/forecast/{toponym}")
async def get_forecaset(
    toponym: str,
    weather_service: WeatherService = Depends(get_weather_service)
) -> dict:
    """
    Locate a toponym and return possible matches with geographical coordinates.
    """
    results = await weather_service.get_query_toponym(toponym)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Toponym was not found")

    top_data = results[0]
    top_location = (top_data.latitude, top_data.longitude)

    forecast = await weather_service.get_weather_forecast(top_location)
    return {"forecast": forecast}
