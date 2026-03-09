from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from care_im.message import IMMessage


class IMBackendBase:
    def __init__(self, fail_silently: bool = False, **kwargs) -> None:
        self.fail_silently = fail_silently

    def send_message(self, message: IMMessage) -> str:
        raise NotImplementedError("send_message() is not implemented")

    def receive_message(self, payload: dict) -> IMMessage:
        raise NotImplementedError("receive_message() is not implemented")
