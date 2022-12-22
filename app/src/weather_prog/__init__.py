"""Package to provide weather forecasts."""
from ._settings import CLI_APP_DIR, Settings
from ._utils import LOG_LEVEL

settings = Settings.get()

__all__ = ["settings", "LOG_LEVEL", "CLI_APP_DIR"]
