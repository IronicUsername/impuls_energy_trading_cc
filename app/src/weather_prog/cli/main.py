"""Package to handle the cli logic of the app."""
import json
import logging
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .. import settings as cli_settings
from .._logging import configure_logging
from ..api import get_weather_forecast_data
from ..api import models as api_models
from ._utils import generate_output, initialize_settings

typer_app = typer.Typer()
_LOGGER = logging.getLogger(__name__)

console = Console()


@typer_app.command()
def forecast(
    location: str = typer.Option(..., "--location", "-l", prompt=True),
    days: Optional[int] = typer.Option(3, "--days", "-d"),
) -> None:
    """Get the input data from the user using the app."""
    query = api_models.WeatherApiQueryParam(key=cli_settings.api_weather_auth_token, days=days, location=location)
    try:
        weather_forecast = get_weather_forecast_data(params=query)
        output_path = generate_output(weather_forecast=weather_forecast)

        msg = typer.style("Result was outputted in this directory:", fg=typer.colors.BRIGHT_WHITE)
        typer.echo(f"{msg} {typer.style(str(output_path), fg=typer.colors.BRIGHT_GREEN)}")
    except Exception as e:
        msg = typer.style("Error:", fg=typer.colors.BRIGHT_WHITE)
        typer.echo(f"{msg} {typer.style(str(e), fg=typer.colors.BRIGHT_RED)}")

    typer.Exit()


@typer_app.command()
def settings(
    open: bool = typer.Option(False, "--open", "-o"),
) -> None:
    """Get the application settings."""
    config_path = initialize_settings()

    if not open:
        table = Table("name", "setting")
        for row_name, row_setting in json.loads(cli_settings.to_cli_json()).items():
            table.add_row(row_name, str(row_setting))
        console.print(table)
        return

    opening_statement = typer.style("Opening config directory:", fg=typer.colors.BRIGHT_WHITE)
    typer.echo(f"{opening_statement} {typer.style(str(config_path), fg=typer.colors.BRIGHT_BLUE)}")
    typer.launch(str(config_path), locate=True)


def run_app() -> None:
    """Start the application."""
    configure_logging(cli_settings.log_level)
    _LOGGER.info(f"Starting {cli_settings.app_name}.")
    typer_app(prog_name=cli_settings.app_name)
    # NOTE: after app finished, nothing after this call will be registered as of now.
