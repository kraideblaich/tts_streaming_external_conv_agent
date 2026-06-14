from __future__ import annotations

import json
import logging
import ssl
from typing import Any, AsyncGenerator, Literal
from pathlib import Path
import aiohttp

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_TIMEOUT, CONF_TOKEN, CONF_URL, CA_CERT_PATH

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ExternalConversationStreamEntity(hass, entry)])


class ExternalConversationStreamEntity(
    conversation.ConversationEntity,
    conversation.AbstractConversationAgent,
):
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_name = "External Conversation Stream"
    _attr_supports_streaming = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._session = async_get_clientsession(hass)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        conversation.async_set_agent(self.hass, self.entry, self)

    async def async_will_remove_from_hass(self) -> None:
        conversation.async_unset_agent(self.hass, self.entry)
        await super().async_will_remove_from_hass()

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        return MATCH_ALL

    @property
    def _url(self) -> str:
        return self.entry.data[CONF_URL]

    @property
    def _token(self) -> str | None:
        return self.entry.data.get(CONF_TOKEN)

    @property
    def _timeout(self) -> int:
        return self.entry.data.get(CONF_TIMEOUT, 180)

    @property
    def _ca_cert_path(self) -> str | None:
        return self.entry.data.get(CA_CERT_PATH, None)

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        continue_conversation = False

        async def delta_stream() -> AsyncGenerator[dict[str, Any], None]:
            nonlocal continue_conversation

            payload = {
                "text": user_input.text,
                "language": user_input.language,
                "conversation_id": user_input.conversation_id,
                "device_id": user_input.device_id,
                "agent_id": user_input.agent_id,
                "extra_system_prompt": user_input.extra_system_prompt,
            }

            headers = {
                "Accept": "application/x-ndjson",
            }
            if self._token:
                headers["Authorization"] = f"Bearer {self._token}"

            ssl_context = None
            if self._ca_cert_path:
                ca_path = Path(self._ca_cert_path)

                if not ca_path.is_file():
                    raise FileNotFoundError(f"CA certificate file not found: {self._ca_cert_path}")

                ssl_context = ssl.create_default_context(
                    cafile=str(ca_path)
                )

            async with self._session.post(
                self._url,
                json=payload,
                headers=headers,
                ssl=ssl_context,
                timeout=aiohttp.ClientTimeout(total=self._timeout),
            ) as resp:
                resp.raise_for_status()

                async for raw_line in resp.content:
                    line = raw_line.decode("utf-8").strip()
                    if not line:
                        continue

                    # Maximale Zeilen-Länge (10KB) zur Vermeidung von Memory-Problemen
                    if len(line) > 10240:
                        _LOGGER.warning("Skipping overly long line in streaming response")
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError as e:
                        _LOGGER.error("Failed to parse JSON in streaming response: %s", e)
                        continue

                    event_type = event.get("type")
                    _LOGGER.debug("Received event: %s", event_type)

                    if event_type == "assistant_start":
                        yield {"role": "assistant"}

                    elif event_type == "assistant_delta":
                        content = event.get("content", "")
                        if content:
                            yield {"content": content}

                    elif event_type == "tool_call":
                        yield {
                            "tool_calls": event["tool_calls"]
                        }

                    elif event_type == "tool_result":
                        yield {
                            "role": "tool_result",
                            "tool_call_id": event["tool_call_id"],
                            "tool_name": event["tool_name"],
                            "tool_result": event["tool_result"],
                        }

                    elif event_type == "done":
                        continue_conversation = bool(
                            event.get("continue_conversation", False)
                        )
                        break

                    else:
                        _LOGGER.warning("Unknown event type received: %s", event_type)

        async for _ in chat_log.async_add_delta_content_stream(
            self.entity_id, delta_stream()
        ):
            pass

        result = conversation.async_get_result_from_chat_log(user_input, chat_log)
        return conversation.ConversationResult(
            response=result.response,
            conversation_id=result.conversation_id,
            continue_conversation=continue_conversation,
        )