from unittest.mock import Mock
import datetime

from weather_app.main import app
from weather_app.services.cache import InMemoryCacheService, get_cache_service
from weather_app.services.weather import \
    WeatherService, Forecast, WeatherType, Temperature, ToponymData, \
    get_weather_service

from fastapi.testclient import TestClient

test_client = TestClient(app)

cache_service = InMemoryCacheService()
weather_service = Mock(spec=WeatherService)

def get_test_cache_service() -> InMemoryCacheService:
    """Returns new in-memory cache service implementation for testing."""
    return cache_service

def get_test_weather_service() -> Mock:
    """Returns mock weather service for testing."""
    return weather_service

def test_get_forecast():
    """Tests get_weather_forecast route."""

    app.dependency_overrides[get_cache_service] = get_test_cache_service
    app.dependency_overrides[get_weather_service] = get_test_weather_service

    weather_service.get_query_toponym.return_value = [
        ToponymData(toponym="Liberec",
                    country="CZ",
                    latitude=50.7772928,
                    longitude=15.0831104)
    ]

    weather_service.get_weather_forecast.return_value = [
        Forecast(reference_time=datetime.datetime.now(),
                 weather_type=WeatherType.CLEAR,
                 temperature=Temperature(10, 5, 15, 12.5))
    ]

    res = test_client.get("/api/v1/weather/forecast/Liberec")
    assert res.status_code == 200

    weather_service.get_weather_forecast.assert_called_once()
    weather_service.get_weather_forecast.assert_called_with(
        (50.7772928, 15.0831104))
