import time

from weather_app.services.cache import InMemoryCacheService
import pytest

@pytest.fixture
def cache() -> InMemoryCacheService:
    """Fixture to create InMemoryCacheService and inject to test cases."""
    return InMemoryCacheService()

#pylint: disable=redefined-outer-name
def test_set_and_get(cache: InMemoryCacheService) -> None:
    """Test setting value in cache (no TTL.)"""
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

#pylint: disable=redefined-outer-name
def test_get_nonexistent_key(cache: InMemoryCacheService) -> None:
    """Test getting missing key."""
    assert cache.get("nonexistent") is None

#pylint: disable=redefined-outer-name
def test_set_with_ttl(cache: InMemoryCacheService) -> None:
    """Test cache expiry (setting with TTL.)"""
    cache.set("key1", "value1", ttl=1)
    assert cache.get("key1") == "value1"
    time.sleep(1.1)
    assert cache.get("key1") is None

#pylint: disable=redefined-outer-name
def test_set_ttl(cache: InMemoryCacheService) -> None:
    """Test updating key TTL."""
    cache.set("key1", "value1")
    cache.set_ttl("key1", 1)
    assert cache.get("key1") == "value1"
    time.sleep(1.1)
    assert cache.get("key1") is None

#pylint: disable=redefined-outer-name
def test_delete(cache: InMemoryCacheService) -> None:
    """Test key deletion."""
    cache.set("key1", "value1")
    cache.delete("key1")
    assert cache.get("key1") is None
