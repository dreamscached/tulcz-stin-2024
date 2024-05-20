"""
Weather services provide weather and geo-related data, such as forecasts,
historical data, geographic name to coordinates mapping, etc.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import datetime
import os

from weather_app.services.cache import CacheService, get_cache_service
from weather_app.services.thread import ThreadPoolService, get_thread_pool_service

from pyowm import OWM
from pyowm.weatherapi25.weather import Weather
from pyowm.weatherapi25.location import Location
from fastapi import Depends

@dataclass
class ToponymData:
    """Common data class for toponym name and coordinate.s"""
    toponym: str
    country: str
    latitude: float
    longitude: float

class WeatherType(Enum):
    """Enum type for various weather types."""
    RAIN = "Rain"
    CLEAR = "Sun"
    FOG = "Fog"
    CLOUDY = "Clouds"
    SNOW = "Snow"
    STORM = "Storm"
    TORNADO = "Tornado"
    HURRICANE = "Hurricane"

@dataclass
class Temperature:
    """Data class for temperature that includes extra data."""
    temperature: float
    min_temperature: float
    max_temperature: float
    feels_like: float

@dataclass
class Forecast:
    """Data class for a forecast details object."""
    reference_time: datetime.datetime
    weather_type: WeatherType
    temperature: Temperature

class TempUnit(Enum):
    """Enum type for temperature units."""
    KELVIN = "kelvin"
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"

class WeatherService(ABC):
    """Abstract class for weather service implementations to extend."""

    @abstractmethod
    async def get_query_toponym(self, toponym: str) -> list[ToponymData]:
        """
        Performs a lookup to retrieve geographical coordinates for a given
        toponym string and returns a list of possible matches.
        """
    @abstractmethod
    async def get_weather_forecast(
        self,
        location: tuple[float, float],
        temp_type: TempUnit = TempUnit.CELSIUS
    ) -> list[Forecast]:
        """
        Performs a forecast fetch for the specified location and returns
        a list of weather forecast details.
        """


def get_weather_service(
    cache: CacheService = Depends(get_cache_service),
    thread_pool: ThreadPoolService = Depends(get_thread_pool_service)
) -> WeatherService:
    """Dependency factory to create instance of WeatherService."""
    api_key = os.environ["APP_OWM_API_KEY"]
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

    async def get_query_toponym(self, toponym: str) -> list[ToponymData]:
        def to_toponym(it: Location) -> ToponymData:
            return ToponymData(it.name, it.country, it.lat, it.lon)

        raw = await self._th_pool.run_in_thread(self._geocode.geocode, toponym)
        return list(map(to_toponym, raw))

    async def get_weather_forecast(
        self,
        location: tuple[float, float],
        temp_type: TempUnit = TempUnit.CELSIUS
    ) -> list[Forecast]:
        forecast_raw = await self._th_pool.run_in_thread(
            self._weather.forecast_at_coords,
            *location, "3h")

        def to_forecast(weather: Weather) -> Forecast:
            temperature_raw = weather.temperature(temp_type.value)
            temperature = Temperature(temperature_raw["temp"],
                                      temperature_raw["temp_min"],
                                      temperature_raw["temp_max"],
                                      temperature_raw["feels_like"])

            return Forecast(weather.ref_time,
                            WeatherType(weather.status),
                            temperature)

        return list(map(to_forecast, forecast_raw.forecast.weathers))
