"""Module that contains the API helper logic."""
import json
import logging

from httpx import ConnectError, ConnectTimeout, QueryParams, get
from httpx._status_codes import codes as httpx_codes

from .. import settings
from . import error, models

_LOGGER = logging.getLogger(__name__)


def get_weather_forecast_data(params: models.WeatherApiQueryParam) -> models.WeatherForecast:
    """Get valid access token for API request.

    The authorization endpoint returns multiple headers, we
    only need the `access_token` to create the typical `Bearer ...` authentication header.
    """
    get_params = QueryParams({**json.loads(params.json(by_alias=True)), "key": settings.api_weather_auth_token})
    try:
        response = get(url=settings.api_weather_forecast_base_url, params=get_params)
    except ConnectError:
        _LOGGER.warning("There was a problem with the connection while fetching the auth credentials.")
        raise error.ApiConnectionError("Couldn't connect to API.")
    except ConnectTimeout:
        _LOGGER.warning("Timeout on auth API fetch.")
        raise error.ApiConnectionTimeout("Timeout on API fetch.")
    except Exception:
        _LOGGER.exception("Something went wrong.")
        raise error.ApiUnknownError("Something went wrong.")

    if response.status_code != httpx_codes.OK:
        raise error.ApiIllegalResponse(f"Could not fetch weather data: {response.status_code} | {response.json()}")

    try:
        return models.WeatherForecast(**response.json())
    except json.JSONDecodeError:
        _LOGGER.exception("Couldn't decode the response.", extra={"response": response})
        raise
