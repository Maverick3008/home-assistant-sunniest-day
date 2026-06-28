"""Constants for the Sonnigster Tag integration."""
from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "sunniest_day"
PLATFORMS: list[Platform] = [Platform.SENSOR]

CONF_WEATHER_ENTITY = "weather_entity"
CONF_LOOKAHEAD_DAYS = "lookahead_days"
CONF_IGNORE_TODAY_AFTER = "ignore_today_after"
CONF_PRECIPITATION_FACTOR = "precipitation_factor"
CONF_UV_FACTOR = "uv_factor"
CONF_UPDATE_INTERVAL_MINUTES = "update_interval_minutes"

DEFAULT_NAME = "Sonnigster Tag"
DEFAULT_LOOKAHEAD_DAYS = 6
DEFAULT_IGNORE_TODAY_AFTER = 15
DEFAULT_PRECIPITATION_FACTOR = 5.0
DEFAULT_UV_FACTOR = 2.0
DEFAULT_UPDATE_INTERVAL_MINUTES = 60
FORECAST_TYPE = "daily"

DEFAULTS = {
    CONF_LOOKAHEAD_DAYS: DEFAULT_LOOKAHEAD_DAYS,
    CONF_IGNORE_TODAY_AFTER: DEFAULT_IGNORE_TODAY_AFTER,
    CONF_PRECIPITATION_FACTOR: DEFAULT_PRECIPITATION_FACTOR,
    CONF_UV_FACTOR: DEFAULT_UV_FACTOR,
    CONF_UPDATE_INTERVAL_MINUTES: DEFAULT_UPDATE_INTERVAL_MINUTES,
}

# Home Assistant weather conditions:
# https://www.home-assistant.io/integrations/weather/#condition-mapping
CONDITION_SCORES: dict[str, float] = {
    "sunny": 100.0,
    "clear-night": 90.0,
    "partlycloudy": 70.0,
    "cloudy": 40.0,
    "windy": 35.0,
    "windy-variant": 30.0,
    "fog": 25.0,
    "rainy": 10.0,
    "pouring": 5.0,
    "snowy": 0.0,
    "snowy-rainy": 0.0,
    "lightning": 0.0,
    "lightning-rainy": 0.0,
    "hail": 0.0,
    "exceptional": 0.0,
}

WEEKDAYS_DE: dict[str, str] = {
    "Monday": "Montag",
    "Tuesday": "Dienstag",
    "Wednesday": "Mittwoch",
    "Thursday": "Donnerstag",
    "Friday": "Freitag",
    "Saturday": "Samstag",
    "Sunday": "Sonntag",
}
