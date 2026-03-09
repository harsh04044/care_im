from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from care_im.backends.base import IMBackendBase


class IMMessage:
    def __init__(
        self,
        content: str = "",
        sender: str | None = None,
        recipient: str = "",
        message_type: str = "text",
        metadata: dict | None = None,
        reply_to: str | None = None,
        platform: str = "whatsapp",
        backend: IMBackendBase | None = None,
        fail_silently: bool = False,
    ) -> None:
        if not isinstance(recipient, str):
            raise ValueError("recipient must be a string, not a list.")

        self.content = content
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.metadata = metadata or {}
        self.reply_to = reply_to
        self.platform = platform
        self.backend = backend
        self.fail_silently = fail_silently

    def dispatch(self, fail_silently: bool = False) -> str:
        effective_fail_silently = fail_silently or self.fail_silently
        if self.backend is None:
            from care_im.utils import get_im_backend

            self.backend = get_im_backend(fail_silently=effective_fail_silently)

        try:
            return self.backend.send_message(self)
        except Exception:
            if not effective_fail_silently:
                raise
            return ""
