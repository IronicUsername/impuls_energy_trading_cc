import json
import logging
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import pydantic

from ._utils import LOG_LEVEL, CliSettings, dict_to_formatted_json_string

_LOGGER = logging.getLogger(__name__)
_PROJECT_ROOT = Path(__file__).parents[2]
CLI_APP_DIR = _PROJECT_ROOT / ".weather_prog"
CLI_OUT_PATH_DEFAULT = CLI_APP_DIR / "output"
CLI_LOG_DIR_DEFAULT = CLI_APP_DIR / "logs"


def json_config_settings_source(settings: pydantic.BaseSettings) -> dict[str, Any]:
    """Load settings from a `config.json` file.

    Here we happen to choose to use the `env_file_encoding` from Config when reading `config.json`
    """

    def _initialize_base_app_data() -> None:
        """Initialize the base structure + empty config.json file for the app."""
        _LOGGER.debug("Initializing config path + empty config.json.")

        # create default folders
        CLI_APP_DIR.mkdir(parents=True, exist_ok=True)
        CLI_OUT_PATH_DEFAULT.mkdir(parents=True, exist_ok=True)
        CLI_LOG_DIR_DEFAULT.mkdir(parents=True, exist_ok=True)

        with open(CLI_APP_DIR / "config.json", "w") as file:
            file.write("{}")

    _LOGGER.debug("Loading settings from config.json.")
    encoding = settings.__config__.env_file_encoding
    file_settings: dict[str, Any] = {}
    try:
        file_settings = json.loads((CLI_APP_DIR / "config.json").read_text(encoding))
    except Exception:
        _LOGGER.debug("Probably couldn't find config.json.")
        _initialize_base_app_data()
    return file_settings


class Settings(pydantic.BaseSettings):
    """Parse environment variables to optionally validate them."""

    app_name: str = "weather_prog"
    version: str = "0.1.0"

    is_dev_mode: bool = bool(sys.flags.dev_mode)
    log_level: str = str(LOG_LEVEL.INFO)
    save_log_to_file: bool = True
    print_logs: bool = False

    api_weather_forecast_base_url: pydantic.HttpUrl = pydantic.parse_obj_as(
        pydantic.HttpUrl, "http://api.weatherapi.com/v1/forecast.json"
    )
    api_weather_auth_token: str = "bea853d469e0444dbe7152331220507"
    cli_out_path: Path = CLI_OUT_PATH_DEFAULT
    cli_log_dir: Path = CLI_LOG_DIR_DEFAULT

    class Config:
        """Config of the app settings."""

        env_file = ".env"
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls,
            init_settings: pydantic.env_settings.InitSettingsSource,
            env_settings: pydantic.env_settings.EnvSettingsSource,
            file_secret_settings: pydantic.env_settings.SecretsSettingsSource,
        ) -> tuple[
            pydantic.env_settings.InitSettingsSource,
            pydantic.env_settings.EnvSettingsSource,
            Callable[[pydantic.BaseSettings], dict[str, Any]],
            pydantic.env_settings.SecretsSettingsSource,
        ]:
            """Customize the setting possibilities.

            More on that: https://docs.pydantic.dev/usage/settings/#adding-sources
            """
            return (init_settings, env_settings, json_config_settings_source, file_secret_settings)

    @pydantic.validator("log_level")
    def check_log_level_name(cls, log_level: str) -> str:
        """Assert that the given log level exists."""
        existing_log_levels = list(logging._nameToLevel)
        if log_level.upper() not in existing_log_levels:
            raise ValueError(f'Must provide an existing log level: {", ".join(existing_log_levels)}')

        return log_level

    @classmethod
    @lru_cache(1)
    def get(cls) -> "Settings":
        """Get a cached Settings file."""
        return cls()

    @classmethod
    def to_cli_json(cls) -> str:
        """Get the application settings as json-string."""
        cli_settings = CliSettings(**json.loads(cls().json()))
        return dict_to_formatted_json_string(data_object=cli_settings.json())
