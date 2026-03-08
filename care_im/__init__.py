"""IM layer for CARE — WhatsApp and the like."""

__all__ = ["IMMessage", "get_im_backend", "send_im_message"]


def __getattr__(name: str):
    if name == "IMMessage":
        from care_im.message import IMMessage

        return IMMessage
    if name == "get_im_backend":
        from care_im.utils import get_im_backend

        return get_im_backend
    if name == "send_im_message":
        from care_im.utils import send_im_message

        return send_im_message
    raise AttributeError(f"module 'care_im' has no attribute {name!r}")
