"""Config flow for Sonnigster Tag."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector

from .const import (
    CONF_IGNORE_TODAY_AFTER,
    CONF_LOOKAHEAD_DAYS,
    CONF_PRECIPITATION_FACTOR,
    CONF_UPDATE_INTERVAL_MINUTES,
    CONF_UV_FACTOR,
    CONF_WEATHER_ENTITY,
    DEFAULT_IGNORE_TODAY_AFTER,
    DEFAULT_LOOKAHEAD_DAYS,
    DEFAULT_NAME,
    DEFAULT_PRECIPITATION_FACTOR,
    DEFAULT_UPDATE_INTERVAL_MINUTES,
    DEFAULT_UV_FACTOR,
    DEFAULTS,
    DOMAIN,
    FORECAST_TYPE,
)


class SunnyDayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sonnigster Tag."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow."""
        return SunnyDayOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_WEATHER_ENTITY])
            self._abort_if_unique_id_configured()

            try:
                await _async_validate_forecast(self.hass, user_input[CONF_WEATHER_ENTITY])
            except NoForecastError:
                errors["base"] = "no_forecast"
            except CannotConnectError:
                errors["base"] = "cannot_connect"
            else:
                title = user_input.get(CONF_NAME) or DEFAULT_NAME
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_initial_schema(),
            errors=errors,
        )


class SunnyDayOptionsFlow(OptionsFlow):
    """Handle options for Sonnigster Tag."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = _merged_options(self.config_entry)
        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(current),
        )


def _initial_schema() -> vol.Schema:
    """Return schema for first setup."""
    return vol.Schema(
        {
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Required(CONF_WEATHER_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="weather")
            ),
            vol.Optional(CONF_LOOKAHEAD_DAYS, default=DEFAULT_LOOKAHEAD_DAYS): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=14,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                CONF_IGNORE_TODAY_AFTER, default=DEFAULT_IGNORE_TODAY_AFTER
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=23,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                CONF_PRECIPITATION_FACTOR, default=DEFAULT_PRECIPITATION_FACTOR
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=20,
                    step=0.5,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(CONF_UV_FACTOR, default=DEFAULT_UV_FACTOR): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=10,
                    step=0.5,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                CONF_UPDATE_INTERVAL_MINUTES,
                default=DEFAULT_UPDATE_INTERVAL_MINUTES,
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=15,
                    max=360,
                    step=15,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="min",
                )
            ),
        }
    )


def _options_schema(current: dict[str, Any]) -> vol.Schema:
    """Return options schema."""
    return vol.Schema(
        {
            vol.Optional(
                CONF_LOOKAHEAD_DAYS,
                default=current[CONF_LOOKAHEAD_DAYS],
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=14,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                CONF_IGNORE_TODAY_AFTER,
                default=current[CONF_IGNORE_TODAY_AFTER],
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=23,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                CONF_PRECIPITATION_FACTOR,
                default=current[CONF_PRECIPITATION_FACTOR],
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=20,
                    step=0.5,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                CONF_UV_FACTOR,
                default=current[CONF_UV_FACTOR],
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=10,
                    step=0.5,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                CONF_UPDATE_INTERVAL_MINUTES,
                default=current[CONF_UPDATE_INTERVAL_MINUTES],
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=15,
                    max=360,
                    step=15,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="min",
                )
            ),
        }
    )


def _merged_options(config_entry: ConfigEntry) -> dict[str, Any]:
    """Merge defaults, entry data and options."""
    merged = dict(DEFAULTS)
    merged.update(config_entry.data)
    merged.update(config_entry.options)
    return merged


async def _async_validate_forecast(hass: HomeAssistant, weather_entity: str) -> None:
    """Validate that the selected weather entity can return a daily forecast."""
    try:
        response = await hass.services.async_call(
            "weather",
            "get_forecasts",
            {"entity_id": weather_entity, "type": FORECAST_TYPE},
            blocking=True,
            return_response=True,
        )
    except HomeAssistantError as err:
        raise CannotConnectError from err

    if not isinstance(response, dict):
        raise NoForecastError

    forecast = response.get(weather_entity, {}).get("forecast")
    if not forecast:
        raise NoForecastError


class CannotConnectError(Exception):
    """Error to indicate we cannot connect."""


class NoForecastError(Exception):
    """Error to indicate that no daily forecast was returned."""
