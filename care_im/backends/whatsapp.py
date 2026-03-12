"""WhatsApp Cloud API. Set WHATSAPP_* in settings."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import requests
from django.conf import settings

from care_im.backends.base import IMBackendBase

if TYPE_CHECKING:
    from care_im.message import IMMessage

GRAPH_API_URL = "https://graph.facebook.com/v21.0"

logger = logging.getLogger(__name__)


def get_webhook_value(body: dict) -> dict:
    entry = body.get("entry", [{}])
    changes = entry[0].get("changes", [{}]) if entry else [{}]
    return changes[0].get("value", {}) if changes else {}


class WhatsAppBackend(IMBackendBase):
    _client = None

    @classmethod
    def _get_client(cls) -> requests.Session:
        if cls._client is None:
            session = requests.Session()
            session.headers.update(
                {
                    "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
                    "Content-Type": "application/json",
                }
            )
            cls._client = session
        return cls._client

    def send_message(self, message: IMMessage) -> str:
        silent = self.fail_silently or getattr(message, "fail_silently", False)
        client = self._get_client()
        client.headers["Authorization"] = f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"
        phone_number_id = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", None) or ""
        if not phone_number_id:
            raise ValueError(
                "WHATSAPP_PHONE_NUMBER_ID is not set. "
                "Add it to .env or export it before running the server."
            )

        payload: dict = {
            "messaging_product": "whatsapp",
            "to": message.recipient,
            "type": message.message_type,
        }

        if message.message_type == "text":
            payload["text"] = {"body": message.content}
        elif message.message_type == "template":
            payload["template"] = message.metadata.get("template", {})
        elif message.message_type == "interactive":
            payload["interactive"] = message.metadata.get("interactive", {})

        if message.reply_to:
            payload["context"] = {"message_id": message.reply_to}

        url = f"{GRAPH_API_URL}/{phone_number_id}/messages"

        try:
            response = client.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["messages"][0]["id"]
        except requests.RequestException as exc:
            if silent:
                status_code = getattr(getattr(exc, "response", None), "status_code", None)
                response_text = getattr(getattr(exc, "response", None), "text", "") or ""
                logger.warning(
                    "WhatsApp send failed (silent). status=%s response=%s",
                    status_code,
                    response_text[:2000],
                )
                return ""
            raise
        except Exception:
            if not silent:
                raise
            return ""

    def receive_message(self, payload: dict) -> IMMessage:
        from care_im.message import IMMessage

        value = get_webhook_value(payload)
        messages = value.get("messages", [{}])
        msg = messages[0] if messages else {}

        content = ""
        message_type = msg.get("type", "text")
        metadata: dict = {"raw": msg}

        if message_type == "text":
            content = msg.get("text", {}).get("body", "")
        elif message_type == "interactive":
            interactive = msg.get("interactive", {})
            reply = interactive.get("button_reply") or interactive.get("list_reply", {})
            content = reply.get("id", "")
            metadata["interactive_id"] = reply.get("id", "")
            metadata["interactive_title"] = reply.get("title", "")

        context = msg.get("context", {})

        return IMMessage(
            content=content,
            sender=msg.get("from", ""),
            recipient=value.get("metadata", {}).get("display_phone_number", ""),
            message_type=message_type,
            metadata=metadata,
            reply_to=context.get("message_id"),
            platform="whatsapp",
        )
