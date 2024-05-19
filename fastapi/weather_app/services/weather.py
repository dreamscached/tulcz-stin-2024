"""
Weather services provide weather and geo-related data, such as forecasts,
historical data, geographic name to coordinates mapping, etc.
"""

from abc import ABC, abstractmethod
from typing import Tuple, List
import os

from weather_app.services.cache import CacheService, get_cache_service
from weather_app.services.thread import ThreadPoolService, get_thread_pool_service

from pyowm import OWM
from pyowm.weatherapi25.location import Location
from fastapi import Depends

GeoCoord = Tuple[float, float]

class WeatherService(ABC):
    """Abstract class for weather service implementations to extend."""

    @abstractmethod
    async def get_toponym_coordinates(self, toponym: str) -> List[GeoCoord]:
        """
        Performs a lookup to retrieve geographical coordinates for a given
        toponym string and returns a list of possible matches.
        """


def get_weather_service(
    cache: CacheService = Depends(get_cache_service),
    thread_pool: ThreadPoolService = Depends(get_thread_pool_service)
) -> WeatherService:
    """Dependency factory to create instance of WeatherService."""
    api_key = os.environ["APP_OWN_API_KEY"]
    return OpenWeatherService(api_key, cache, thread_pool)


class OpenWeatherService(WeatherService):
    """An implementation of WeatherService that uses OpenWeatherMap API."""

    def __init__(self,
        api_key: str,
        cache: CacheService,
        thread_pool: ThreadPoolService
    ) -> None:
        self._owm = OWM(api_key)
        self._weather = self._owm.weather_manager()
        self._geocode = self._owm.geocoding_manager()

        self._cache = cache
        self._th_pool = thread_pool

    async def get_toponym_coordinates(self, toponym: str) -> List[GeoCoord]:
        def to_geo_coord(it: Location) -> GeoCoord:
            return (it.lat, it.lon)

        raw = await self._th_pool.run_in_thread(self._geocode.geocode, toponym)
        return list(map(to_geo_coord, raw))
