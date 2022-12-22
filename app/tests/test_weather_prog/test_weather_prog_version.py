"""Module to test weather_prog package."""
from weather_prog import settings


def test_version() -> None:
    assert settings.version == "0.1.0"
