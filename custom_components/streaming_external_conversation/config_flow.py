"""Config flow for External Conversation Agent."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_NAME, CONF_TIMEOUT, CONF_TOKEN, CONF_URL, DOMAIN, CA_CERT_PATH

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_URL): vol.All(str, vol.Length(min=1)),
        vol.Optional(CONF_TOKEN): str,
        vol.Optional(CONF_TIMEOUT, default=180): vol.All(vol.Coerce(int), vol.Range(min=10, max=600)),
        vol.Optional(CA_CERT_PATH, default="") : str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for External Conversation Agent."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        return self.async_create_entry(
            title=user_input[CONF_NAME],
            data=user_input,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """External Conversation Agent options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                title=user_input.get(CONF_NAME, self._config_entry.title),
                data={**self._config_entry.data, **user_input},
            )
            return self.async_create_entry(title="", data=user_input)

        current = self._config_entry.data
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=current.get(CONF_NAME, "")): str,
                    vol.Required(CONF_URL, default=current.get(CONF_URL, "")): vol.All(str, vol.Length(min=1)),
                    vol.Optional(CONF_TOKEN, default=current.get(CONF_TOKEN, "")): str,
                    vol.Optional(CONF_TIMEOUT, default=current.get(CONF_TIMEOUT, 180)): vol.All(vol.Coerce(int), vol.Range(min=10, max=600)),
                }
            ),
        )
