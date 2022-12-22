import json
from enum import Enum, auto
from pathlib import Path
from typing import Any, Union

import pydantic


class CliSettings(pydantic.BaseModel):
    """Model the data for the cli config file."""

    log_level: str
    save_log_to_file: bool
    api_weather_forecast_base_url: pydantic.HttpUrl
    api_weather_auth_token: str
    cli_out_path: Path


class LOG_LEVEL(str, Enum):
    """Describe available log levels.

    Reference: https://docs.python.org/3/library/logging.html#logging-levels
    """

    CRITICAL = auto()
    ERROR = auto()
    INFO = auto()
    WARNING = auto()
    DEBUG = auto()
    NOTSET = auto()

    def __str__(self) -> str:
        """Convert enum to string."""
        return f"{self.name}"


def dict_to_formatted_json_string(data_object: Union[dict[str, Any], str]) -> str:
    """Format a given dict to a formated json string.

    Commonly used for printing to cli.
    """
    if isinstance(data_object, dict):
        data_object = json.dumps(data_object)

    return json.dumps(json.loads(data_object), ensure_ascii=False, indent=2, separators=(",", ": "))
