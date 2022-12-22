import csv
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from .. import CLI_APP_DIR, settings
from .._utils import dict_to_formatted_json_string
from ..api import models as api_models

_LOGGER = logging.getLogger(__name__)


def initialize_settings() -> Path:
    """Initialize the config.json, that can later be used to set certain parameters for the cli app."""

    def _get_file_as_dict(path: Path, encoding: str = "utf-8") -> dict[str, Any]:
        data = {}
        with open(path, "r", encoding=encoding) as file:
            data = json.load(file)
        return data

    def _is_data_in_file(path: Path) -> bool:
        return bool(_get_file_as_dict(path=path))

    def _is_settings_data_outdated(path: Path) -> bool:
        data = _get_file_as_dict(path=path)
        cli_settings_dict: dict[str, Any] = json.loads(settings.to_cli_json())

        unique_unified_keys = set(list(data.keys()) + list(cli_settings_dict.keys()))
        for key in unique_unified_keys:
            if data.get(key) != cli_settings_dict.get(key):
                return False
        return True

    def _overwrite_empty_settings_data_to_file(path: Path) -> None:
        with open(path, "r+", encoding="utf-8") as file:
            file.seek(0)
            file.write(settings.to_cli_json())
            file.truncate()

    _LOGGER.info("Initializing settings.")
    config_path = CLI_APP_DIR / "config.json"

    if config_path.is_file():
        _LOGGER.warn("The config file config.json does not exist. Creating....")
        if not _is_data_in_file(path=config_path) or _is_settings_data_outdated(path=config_path):
            _overwrite_empty_settings_data_to_file(path=config_path)

    _LOGGER.info("Settings file config.json successfully found.", extra={"config_path": config_path})
    return config_path


def generate_output(weather_forecast: api_models.WeatherForecast) -> Path:
    """Generate 2 different output files and return the base output path.

    Generates:
    - `.csv` file
    - `.json` file
    """
    encoding, filename = "utf-8", "weather_prog_result"
    output_start_timestamp = int(time.mktime(datetime.now().timetuple()))

    result_folder_name = f"{settings.app_name}_result_{output_start_timestamp}"
    out_path = settings.cli_out_path / result_folder_name
    out_path.mkdir(parents=True, exist_ok=True)

    # write result json file
    with open(out_path / f"{filename}.json", "w", encoding=encoding) as out_file:
        out_file.write(dict_to_formatted_json_string(weather_forecast.json()))

    # write result txt file
    fieldnames = [
        *list(api_models.WeatherApiResponseForecastDayHour.schema()["properties"].keys()),
        *list(api_models.WeatherApiResponseLocation.schema()["properties"].keys()),
    ]
    with open(out_path / f"{filename}.csv", "w", encoding=encoding, newline="") as out_file:
        csv_writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for day in weather_forecast.forecast.forecastday:
            for hour in day.hour:
                data_to_write = {
                    **json.loads(hour.json()),
                    **json.loads(weather_forecast.location.json()),
                }
                csv_writer.writerow(data_to_write)

    _LOGGER.info("Generating output.", extra={"weather_forecast": weather_forecast})
    return out_path
