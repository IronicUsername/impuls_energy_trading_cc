"""Package to hold the API data models."""
import pydantic


class WeatherApiQueryParam(pydantic.BaseModel):
    """Describe api query."""

    days: int
    location: str = pydantic.Field(..., alias="q")

    class Config:
        """Set the pydantic BaseModel up."""

        allow_population_by_field_name = True


class WeatherApiResponseForecastDayHour(pydantic.BaseModel):
    """Describe a weather forecast day hour."""

    temp_c: float
    wind_kph: float
    cloud: int
    time: str


class WeatherApiResponseForecastDay(pydantic.BaseModel):
    """Describe the single weather forecast hour."""

    date: str
    hour: list[WeatherApiResponseForecastDayHour]


class WeatherApiResponseForecast(pydantic.BaseModel):
    """Describe the wrapper entity for a forecast day hour."""

    forecastday: list[WeatherApiResponseForecastDay]


class WeatherApiResponseLocation(pydantic.BaseModel):
    """Describe the detail information for a weather forecast location."""

    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str
    localtime: str


class WeatherForecast(pydantic.BaseModel):
    """Describe a the weather forecast data locations."""

    location: WeatherApiResponseLocation
    forecast: WeatherApiResponseForecast
