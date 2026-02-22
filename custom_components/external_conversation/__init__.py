"""External Conversation Agent integration."""
from __future__ import annotations

import logging
from typing import Literal

import aiohttp

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, intent
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_TOKEN, CONF_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up External Conversation Agent from a config entry."""
    session = async_get_clientsession(hass)
    agent = ExternalConversationAgent(hass, entry, session)
    conversation.async_set_agent(hass, entry, agent)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    conversation.async_unset_agent(hass, entry)
    return True


class ExternalConversationAgent(conversation.AbstractConversationAgent):
    """Conversation agent that forwards requests to an external HTTP endpoint.

    The endpoint receives a JSON payload describing the conversation turn and
    must return a JSON response with the agent's reply.

    Request payload:
        {
            "text": str,                  # user's message
            "language": str,              # e.g. "en"
            "conversation_id": str|null,  # opaque ID for multi-turn context
            "device_id": str|null,
            "agent_id": str
        }

    Expected response:
        {
            "message": str,               # text to speak back to the user
            "continue_conversation": bool # true to keep the mic open
        }
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self._session = session

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return supported languages."""
        return MATCH_ALL

    @property
    def _url(self) -> str:
        return self.entry.data[CONF_URL]

    @property
    def _token(self) -> str | None:
        return self.entry.data.get(CONF_TOKEN)

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Forward the conversation turn to the external endpoint."""
        payload = {
            "text": user_input.text,
            "language": user_input.language,
            "conversation_id": user_input.conversation_id,
            "device_id": user_input.device_id,
            "agent_id": user_input.agent_id,
        }

        headers = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        intent_response = intent.IntentResponse(language=user_input.language)
        continue_conversation = False

        try:
            async with self._session.post(
                self._url, json=payload, headers=headers
            ) as resp:
                if not resp.ok:
                    body = await resp.text()
                    _LOGGER.error("External agent returned %s: %s", resp.status, body)
                resp.raise_for_status()
                data = await resp.json()

            message = data["message"]
            continue_conversation = bool(data.get("continue_conversation", False))
            intent_response.async_set_speech(message)

        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to external agent at %s: %s", self._url, err)
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                "Sorry, I couldn't reach the external conversation service.",
            )
        except (KeyError, ValueError) as err:
            _LOGGER.error("Unexpected response from external agent: %s", err)
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                "Sorry, the external conversation service returned an unexpected response.",
            )

        return conversation.ConversationResult(
            response=intent_response,
            conversation_id=user_input.conversation_id,
            continue_conversation=continue_conversation,
        )
