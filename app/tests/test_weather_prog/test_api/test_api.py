from typing import Any, Callable, ContextManager, Dict, Optional

import pytest
import respx
from httpx import ConnectError, ConnectTimeout, Response
from respx import Route

from weather_prog import settings
from weather_prog.api import error as weather_prog_api_error
from weather_prog.api import get_weather_forecast_data
from weather_prog.api import models as weather_prog_api_models


@respx.mock
def test_get_weather_forecast_data_successful(
    mock_weather_data_api: Callable[[Optional[Response]], ContextManager[Dict[str, Route]]],
    sample_successful_query: weather_prog_api_models.WeatherApiQueryParam,
) -> None:
    with mock_weather_data_api(None):
        forecast = get_weather_forecast_data(params=sample_successful_query())

        assert len(forecast.forecast.forecastday) == 3
        assert forecast.forecast.forecastday[0].date == "2022-12-22"
        assert forecast.forecast.forecastday[1].date == "2022-12-23"
        assert forecast.forecast.forecastday[2].date == "2022-12-24"
        assert (
            len(forecast.forecast.forecastday[0].hour)
            == len(forecast.forecast.forecastday[1].hour)
            == len(forecast.forecast.forecastday[2].hour)
            == 24
        )

        assert forecast.location.country == "USA"
        assert forecast.location.lat == 40.71
        assert forecast.location.lon == -74.21
        assert forecast.location.localtime == "2022-12-22 15:10"
        assert forecast.location.name == "Newark"
        assert forecast.location.region == "New Jersey"
        assert forecast.location.tz_id == "America/New_York"


@respx.mock
def test_get_weather_forecast_data_unsuccessful_404(
    mock_weather_data_api: Callable[[Optional[Response]], ContextManager[Dict[str, Route]]],
    sample_successful_query: weather_prog_api_models.WeatherApiQueryParam,
) -> None:
    mock_response = Response(status_code=404, json={"Details": "Error."})
    with mock_weather_data_api(mock_response):
        with pytest.raises(weather_prog_api_error.ApiIllegalResponse) as exc_info:
            get_weather_forecast_data(params=sample_successful_query())

        assert len(exc_info.value.args) == 1
        assert exc_info.value.args[0] == f"Could not fetch weather data: 404 | {mock_response.json()}"


@pytest.mark.parametrize(
    "error_type_input,error_type_output,error_message",
    [
        pytest.param(
            ConnectError,
            weather_prog_api_error.ApiConnectionError,
            "Couldn't connect to API.",
            id="Test edge case `ConnectTimeout`.",
        ),
        pytest.param(
            ConnectTimeout,
            weather_prog_api_error.ApiConnectionTimeout,
            "Timeout on API fetch.",
            id="Timeout on API fetch.",
        ),
        pytest.param(
            Exception,
            weather_prog_api_error.ApiUnknownError,
            "Something went wrong.",
            id="Test edge case `ConnectTimeout`.",
        ),
    ],
)
@respx.mock
def test_get_weather_forecast_data_unsuccessful_api_connection_edge_cases(
    sample_successful_query: weather_prog_api_models.WeatherApiQueryParam,
    error_type_input: Any,
    error_type_output: Any,
    error_message: str,
) -> None:
    # setup
    respx.get(url=settings.api_weather_forecast_base_url, path__startswith="/", name="get_weather_api").mock(
        side_effect=error_type_input
    )
    # action
    with pytest.raises(error_type_output) as exc_info:
        get_weather_forecast_data(params=sample_successful_query())
    assert len(exc_info.value.args) == 1
    assert exc_info.value.args[0] == error_message
