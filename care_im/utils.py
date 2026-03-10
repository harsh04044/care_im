from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.utils.module_loading import import_string

from care_im.message import IMMessage

if TYPE_CHECKING:
    from care_im.backends.base import IMBackendBase


def initialize_backend(
    backend_name: str | None = None,
    fail_silently: bool = False,
    **kwargs,
) -> IMBackendBase:
    backend_class = import_string(backend_name or settings.IM_BACKEND)
    return backend_class(fail_silently=fail_silently, **kwargs)


def get_im_backend(
    backend_name: str | None = None,
    fail_silently: bool = False,
    **kwargs,
) -> IMBackendBase:
    return initialize_backend(
        backend_name=backend_name or getattr(settings, "IM_BACKEND", None),
        fail_silently=fail_silently,
        **kwargs,
    )


def send_im_message(
    content: str,
    recipient: str,
    message_type: str = "text",
    platform: str = "whatsapp",
    sender: str | None = None,
    metadata: dict | None = None,
    reply_to: str | None = None,
    fail_silently: bool = False,
    backend_instance: IMBackendBase | None = None,
) -> str:
    message = IMMessage(
        content=content,
        sender=sender,
        recipient=recipient,
        message_type=message_type,
        metadata=metadata,
        reply_to=reply_to,
        platform=platform,
        backend=backend_instance,
        fail_silently=fail_silently,
    )
    return message.dispatch(fail_silently=fail_silently)
