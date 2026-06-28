"""Coordinator and forecast scoring for Sonnigster Tag."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CONDITION_SCORES,
    CONF_IGNORE_TODAY_AFTER,
    CONF_LOOKAHEAD_DAYS,
    CONF_PRECIPITATION_FACTOR,
    CONF_UPDATE_INTERVAL_MINUTES,
    CONF_UV_FACTOR,
    CONF_WEATHER_ENTITY,
    DEFAULTS,
    DOMAIN,
    FORECAST_TYPE,
    WEEKDAYS_DE,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class BestDay:
    """Calculated best sunny day."""

    forecast: dict[str, Any]
    local_datetime: datetime
    score: float

    @property
    def weekday_de(self) -> str:
        """Return the German weekday name."""
        return WEEKDAYS_DE.get(self.local_datetime.strftime("%A"), self.local_datetime.strftime("%A"))

    @property
    def weekday_with_date_de(self) -> str:
        """Return German weekday plus dd.mm."""
        return f"{self.weekday_de} {self.local_datetime.strftime('%d.%m')}"


@dataclass(slots=True)
class SunnyDayData:
    """Data stored by the coordinator."""

    forecast: list[dict[str, Any]]
    best_day: BestDay | None
    last_update: datetime


class SunnyDayCoordinator(DataUpdateCoordinator[SunnyDayData]):
    """Fetch weather forecasts and calculate the sunniest day."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.entry = entry
        self.weather_entity: str = entry.data[CONF_WEATHER_ENTITY]
        options = self.options

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                minutes=int(options[CONF_UPDATE_INTERVAL_MINUTES])
            ),
        )

    @property
    def options(self) -> dict[str, Any]:
        """Return data and options merged with defaults."""
        merged = dict(DEFAULTS)
        merged.update(self.entry.data)
        merged.update(self.entry.options)
        return merged

    async def _async_update_data(self) -> SunnyDayData:
        """Fetch data from Home Assistant weather forecast service."""
        try:
            response = await self.hass.services.async_call(
                "weather",
                "get_forecasts",
                {"entity_id": self.weather_entity, "type": FORECAST_TYPE},
                blocking=True,
                return_response=True,
            )
        except HomeAssistantError as err:
            raise UpdateFailed(f"weather.get_forecasts failed: {err}") from err

        raw = response.get(self.weather_entity, {}) if isinstance(response, dict) else {}
        forecast = raw.get("forecast", [])
        if forecast is None:
            forecast = []

        # Ensure all entries are normal dicts; some services may return mapping-like objects.
        forecast_list = [dict(item) for item in forecast if isinstance(item, dict)]
        best_day = calculate_best_day(forecast_list, self.options)

        return SunnyDayData(
            forecast=forecast_list,
            best_day=best_day,
            last_update=dt_util.utcnow(),
        )


def calculate_best_day(
    forecast: list[dict[str, Any]],
    options: dict[str, Any],
    now: datetime | None = None,
) -> BestDay | None:
    """Calculate the best sunny day from a daily forecast list."""
    if not forecast:
        return None

    local_now = dt_util.as_local(now or dt_util.now())
    today = local_now.date()
    current_hour = local_now.hour

    lookahead_days = int(options[CONF_LOOKAHEAD_DAYS])
    ignore_today_after = int(options[CONF_IGNORE_TODAY_AFTER])
    precipitation_factor = float(options[CONF_PRECIPITATION_FACTOR])
    uv_factor = float(options[CONF_UV_FACTOR])

    best: BestDay | None = None

    for day in forecast[:lookahead_days]:
        dt_value = day.get("datetime")
        if not dt_value:
            continue

        local_dt = _parse_forecast_datetime(dt_value)
        if local_dt is None:
            continue

        # Same behavior as your template: after the configured hour, ignore today.
        if current_hour >= ignore_today_after and local_dt.date() == today:
            continue

        score = _score_forecast(day, precipitation_factor, uv_factor)

        if best is None or score > best.score:
            best = BestDay(forecast=day, local_datetime=local_dt, score=score)

    return best


def _parse_forecast_datetime(value: Any) -> datetime | None:
    """Parse and localize a forecast datetime value."""
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        parsed = dt_util.parse_datetime(value)
    else:
        return None

    if parsed is None:
        return None
    return dt_util.as_local(parsed)


def _score_forecast(
    day: dict[str, Any], precipitation_factor: float, uv_factor: float
) -> float:
    """Score a single forecast day."""
    condition = str(day.get("condition") or "")
    score = CONDITION_SCORES.get(condition, 0.0)

    precipitation = _float_from_forecast(
        day,
        "precipitation",
        "native_precipitation",
        default=0.0,
    )
    uv_index = _float_from_forecast(day, "uv_index", "uv", default=0.0)

    score -= precipitation * precipitation_factor
    score += uv_index * uv_factor
    return round(score, 2)


def _float_from_forecast(
    day: dict[str, Any], *keys: str, default: float = 0.0
) -> float:
    """Return the first numeric value from the given forecast keys."""
    for key in keys:
        value = day.get(key)
        if value in (None, "", "unknown", "unavailable"):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return default
