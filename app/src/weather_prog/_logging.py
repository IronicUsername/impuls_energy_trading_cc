"""Module that handles logger setup."""
import logging
from datetime import date

from pythonjsonlogger import jsonlogger

from . import LOG_LEVEL, settings

# Adapted from https://docs.python.org/3.9/library/logging.html#logrecord-attributes
LOG_FORMAT = "%(asctime)%(levelname)%(message)%(name)"
LOG_FORMATTER = jsonlogger.JsonFormatter(LOG_FORMAT)


def _raise_test_plugin_logging_level_to_error() -> None:
    """Raise the default test plugin logging level to `ERROR`.

    Some test plugin loggers have a default logging level of `debug`. This severely hinders
    debug-ability of code, since test plugin logs will swamp `stdout` if any test fails.

    To resolve this, we raise the default logging level of test plugin to `ERROR` here.

    """
    logging.getLogger("flake8").setLevel(logging.ERROR)
    logging.getLogger("filelock").setLevel(logging.ERROR)


def configure_logging(log_level: str) -> None:
    """Configure the project logging.

    This function configures the project logging, all loggers instantiated after calling
    this function will inherit this configuration.

    This function should be called at the very start of running the application, else loggers
    with different configurations may be instantiated.

    """
    _raise_test_plugin_logging_level_to_error()

    log_handler = logging.StreamHandler()
    log_handler.setFormatter(LOG_FORMATTER)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(str(LOG_LEVEL.NOTSET))

    # set for every case the log output
    # no log output when these criterions hit
    whitelisted_log_levels = [LOG_LEVEL.CRITICAL, LOG_LEVEL.DEBUG, LOG_LEVEL.ERROR, LOG_LEVEL.WARNING]
    if LOG_LEVEL[log_level] in whitelisted_log_levels or settings.is_dev_mode or settings.print_logs:
        root_logger.addHandler(log_handler)

    # add logging to file
    if settings.save_log_to_file:
        file_name = f"{date.today().isoformat()}_{settings.app_name}_log.json"
        file_handler = logging.FileHandler(settings.cli_log_dir / file_name)
        file_handler.setFormatter(LOG_FORMATTER)
        root_logger.addHandler(file_handler)

    # set our logger to same level as main application running
    logging.getLogger("typer").setLevel(log_level)
