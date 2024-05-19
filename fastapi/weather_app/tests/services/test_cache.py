"""Tests CacheService implementations."""

from typing import Any
import time

import pytest

from weather_app.services.cache import InMemoryCacheService

@pytest.fixture
def cache() -> InMemoryCacheService:
    """Fixture to create InMemoryCacheService and inject to test cases."""
    return InMemoryCacheService()


@pytest.mark.parametrize("key, value", [
    ("key", "value"),
    ("key", None),
    ("key", 42),
    ("key", 3.14),
    ("key", True),
    ("key", [3.14, 2.79]),
    ("key", [3.14, 42]),
    ("key", {"foo": "bar"}),
    ("key", {"foo": "bar", "baz": 3.14}),
    ("", "value"),
    (None, "value")
])
def test_set_nottl(
    #pylint: disable=redefined-outer-name
    cache: InMemoryCacheService,
    key: str,
    value: Any
) -> None:
    """Test setting value in cache (no TTL.)"""
    cache.set(key, value)
    assert cache.get(key) == value

#pylint: disable=redefined-outer-name
def test_get_nonexistent_key(cache: InMemoryCacheService) -> None:
    """Test getting missing key."""
    assert cache.get("nonexistent") is None

@pytest.mark.parametrize("key, value, ttl", [
    ("key", "value", 1),
    ("key", "value", 0),
    ("key", "value", None),
])
def test_set_with_ttl(
    #pylint: disable=redefined-outer-name
    cache: InMemoryCacheService,
    key: str,
    value: Any,
    ttl: int | None
) -> None:
    """Test cache expiry (setting with TTL.)"""
    cache.set(key, value, ttl)
    assert cache.get(key) == value
    if ttl is not None:
        time.sleep(ttl + 0.1)
        assert cache.get(key) is None

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

#pylint: disable=redefined-outer-name
def test_delete_nonexistent(cache: InMemoryCacheService) -> None:
    """Test key deletion of nonexistent key."""
    cache.delete("nonexistent")
