"""Prints to stdout when you don't have WhatsApp creds (dev/tests)."""

from __future__ import annotations

import sys
import threading
import uuid
from typing import TYPE_CHECKING

from care_im.backends.base import IMBackendBase

if TYPE_CHECKING:
    from care_im.message import IMMessage


class ConsoleIMBackend(IMBackendBase):
    def __init__(self, *args, stream=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.stream = stream or sys.stdout
        self._lock = threading.RLock()

    def send_message(self, message: IMMessage) -> str:
        message_id = uuid.uuid4().hex
        with self._lock:
            self.stream.write("-" * 40 + "\n")
            self.stream.write(f"Platform: {message.platform}\n")
            self.stream.write(f"From: {message.sender}\n")
            self.stream.write(f"To: {message.recipient}\n")
            self.stream.write(f"Type: {message.message_type}\n")
            self.stream.write(f"Content: {message.content}\n")
            if message.reply_to:
                self.stream.write(f"Reply-To: {message.reply_to}\n")
            if message.metadata:
                self.stream.write(f"Metadata: {message.metadata}\n")
            self.stream.write(f"Message-ID: {message_id}\n")
            self.stream.write("-" * 40 + "\n")
            self.stream.flush()
        return message_id

    def receive_message(self, payload: dict) -> IMMessage:
        from care_im.message import IMMessage

        return IMMessage(
            content=payload.get("content", ""),
            sender=payload.get("sender", ""),
            recipient=payload.get("recipient", ""),
            message_type=payload.get("message_type", "text"),
            metadata=payload.get("metadata", {}),
            reply_to=payload.get("reply_to"),
            platform=payload.get("platform", "console"),
        )
