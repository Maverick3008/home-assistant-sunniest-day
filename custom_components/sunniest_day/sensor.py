"""Sensor platform for Sonnigster Tag."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_WEATHER_ENTITY, DEFAULT_NAME, DOMAIN
from .coordinator import SunnyDayCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sonnigster Tag sensors."""
    coordinator: SunnyDayCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            BestSunnyDaySensor(coordinator, entry),
            BestSunnyDayWithDateSensor(coordinator, entry),
            ForecastDiagnosticSensor(coordinator, entry),
        ]
    )


class SunnyDaySensorBase(CoordinatorEntity[SunnyDayCoordinator], SensorEntity):
    """Base sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SunnyDayCoordinator, entry: ConfigEntry) -> None:
        """Initialize base sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self.device_name = entry.title or DEFAULT_NAME
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=self.device_name,
            manufacturer="Custom Integration",
            model="Weather Forecast Scorer",
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None

    @property
    def _best_attrs(self) -> dict[str, Any]:
        """Return common attributes for the calculated best day."""
        data = self.coordinator.data
        best = data.best_day if data else None
        if best is None:
            return {
                "weather_entity": self.coordinator.weather_entity,
                "reason": "no_matching_forecast",
            }

        forecast = best.forecast
        return {
            "weather_entity": self.coordinator.weather_entity,
            "datetime": best.local_datetime.isoformat(),
            "score": best.score,
            "condition": forecast.get("condition"),
            "precipitation": forecast.get("precipitation", forecast.get("native_precipitation")),
            "uv_index": forecast.get("uv_index", forecast.get("uv")),
            "temperature": forecast.get("temperature", forecast.get("native_temperature")),
            "templow": forecast.get("templow", forecast.get("native_templow")),
        }


class BestSunnyDaySensor(SunnyDaySensorBase):
    """Sensor for best sunny weekday."""

    _attr_name = None
    _attr_icon = "mdi:white-balance-sunny"

    def __init__(self, coordinator: SunnyDayCoordinator, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_best_day"

    @property
    def native_value(self) -> str | None:
        """Return the German weekday."""
        data = self.coordinator.data
        best = data.best_day if data else None
        return best.weekday_de if best else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return self._best_attrs


class BestSunnyDayWithDateSensor(SunnyDaySensorBase):
    """Sensor for best sunny day with date."""

    _attr_name = "Mit Datum"
    _attr_icon = "mdi:calendar-star"

    def __init__(self, coordinator: SunnyDayCoordinator, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_best_day_with_date"

    @property
    def native_value(self) -> str | None:
        """Return the German weekday plus date."""
        data = self.coordinator.data
        best = data.best_day if data else None
        return best.weekday_with_date_de if best else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return self._best_attrs


class ForecastDiagnosticSensor(SunnyDaySensorBase):
    """Diagnostic sensor that exposes the fetched forecast as attribute."""

    _attr_name = "Wettervorhersage"
    _attr_icon = "mdi:calendar-range"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SunnyDayCoordinator, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_forecast"

    @property
    def native_value(self) -> str | None:
        """Return last update timestamp."""
        data = self.coordinator.data
        return data.last_update.isoformat() if data else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return forecast attributes."""
        data = self.coordinator.data
        return {
            "weather_entity": self.coordinator.weather_entity,
            "forecast": data.forecast if data else [],
        }
