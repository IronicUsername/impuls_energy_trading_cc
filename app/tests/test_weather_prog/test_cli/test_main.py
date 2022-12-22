from typing import Callable, ContextManager, Dict, Optional

import respx
from httpx import Response
from respx import Route
from typer.testing import CliRunner

from weather_prog.api import models as weather_prog_api_models
from weather_prog.cli.main import typer_app

runner = CliRunner()


@respx.mock
def test_forecast_successful(
    mock_weather_data_api: Callable[[Optional[Response]], ContextManager[Dict[str, Route]]],
    sample_successful_query: weather_prog_api_models.WeatherApiQueryParam,
) -> None:
    with mock_weather_data_api(None):
        forecast = runner.invoke(typer_app, ["forecast", "-l", "07112"])

        assert forecast.exit_code == 0
        assert "Result was outputted in this directory:" in forecast.stdout


@respx.mock
def test_forecast_unsuccessful_no_api_connection(
    mock_weather_data_api: Callable[[Optional[Response]], ContextManager[Dict[str, Route]]]
) -> None:
    mock_response = Response(status_code=404, json={"Details": "Error."})
    with mock_weather_data_api(mock_response):
        forecast = runner.invoke(typer_app, ["forecast", "-l", "07112"])

        assert forecast.exit_code == 0
        assert (
            forecast.stdout
            == "Error: ApiIllegalResponse, Could not fetch weather data: 404 | {'Details': 'Error.'} \n"
        )
