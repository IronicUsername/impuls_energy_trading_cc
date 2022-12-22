"""Configure and setup testing of the service."""
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, ContextManager, Dict, Generator, List, Optional

import pytest
import respx
from httpx import Request, Response
from respx import Route

from weather_prog import settings
from weather_prog.api import models as weather_prog_api_models

from . import models as test_models


@pytest.fixture(autouse=True)
def set_necessary_settings(
    patch_settings: Callable[[List[test_models.PatchSetting]], ContextManager[None]], tmp_path: Path
) -> Generator[None, None, None]:
    """Set settings for testing environment."""
    temp_out_path = tmp_path / "output"
    temp_out_path.mkdir(parents=True, exist_ok=True)

    settings_to_patch = [
        test_models.PatchSetting(name="cli_out_path", new_setting=temp_out_path, cached_setting=settings.cli_out_path),
        test_models.PatchSetting(
            name="api_weather_auth_token",
            new_setting="some_auth_token",
            cached_setting=settings.api_weather_auth_token,
        ),
        test_models.PatchSetting(name="save_log_to_file", new_setting=False, cached_setting=settings.save_log_to_file),
    ]

    with patch_settings(settings_to_patch):
        yield


@pytest.fixture
def patch_settings() -> Callable[[List[test_models.PatchSetting]], ContextManager[None]]:
    """Set a new value in settings and reset afterwards."""

    @contextmanager
    def _patch(settings_to_patch: List[test_models.PatchSetting]) -> Generator[None, None, None]:
        for setting in settings_to_patch:
            setattr(settings, setting.name, setting.new_setting)
        yield
        for setting in settings_to_patch:
            setattr(settings, setting.name, setting.cached_setting)

    return _patch


@pytest.fixture
def mock_weather_data_api() -> Callable[[Optional[Response]], ContextManager[Dict[str, Route]]]:
    """Mock API for the auth API."""

    @contextmanager
    def mock_weather_data_api(custom_response: Optional[Response]) -> Generator[Dict[str, Route], None, None]:
        def _dynamic_message_response(request: Request) -> Response:
            if custom_response:
                return custom_response
            return Response(200, json=test_models.SAMPLE_WEATHERAPI_RESPONSE_SUCCESSFULL)

        route_weather_forecast_api = respx.get(
            url=settings.api_weather_forecast_base_url, name="weather_forecast_api"
        ).mock(side_effect=_dynamic_message_response)
        yield {"weather_forecast_api": route_weather_forecast_api}

    return mock_weather_data_api


@pytest.fixture
def sample_successful_query() -> Callable[[int, str], weather_prog_api_models.WeatherApiQueryParam]:
    """Generate a sample API sample query."""

    def _sample_successful_query(days: int = 3, q: str = "07112") -> weather_prog_api_models.WeatherApiQueryParam:
        return weather_prog_api_models.WeatherApiQueryParam(days=days, q=q)

    return _sample_successful_query
