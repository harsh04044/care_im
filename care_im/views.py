from __future__ import annotations

import json
import logging

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from care_im.care_poc import get_care_reply
from care_im.utils import get_im_backend, send_im_message

# TODO(auth): Integrate CARE auth - Service Account token; patient = phone + DoB.

logger = logging.getLogger(__name__)


def _get_whatsapp_backend():
    backend = get_im_backend()
    from care_im.backends.whatsapp import WhatsAppBackend

    if not isinstance(backend, WhatsAppBackend):
        return None
    return backend


@csrf_exempt
@require_http_methods(["GET", "POST"])
def whatsapp_webhook(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge", "")
        verify_token = getattr(settings, "WHATSAPP_VERIFY_TOKEN", "")
        if mode == "subscribe" and token == verify_token:
            return HttpResponse(challenge, content_type="text/plain")
        return HttpResponse("Verification failed", status=403)

    return _whatsapp_webhook_receive(request)


def _handle_status_update(statuses: list[dict]) -> None:
    for s in statuses:
        logger.info(
            "WhatsApp status: %s -> %s (recipient: %s)",
            s.get("id", "?"),
            s.get("status", "?"),
            s.get("recipient_id", "?"),
        )


def _whatsapp_webhook_receive(request: HttpRequest) -> HttpResponse:
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        logger.warning("WhatsApp webhook: invalid JSON body")
        return HttpResponse(status=200)

    if body.get("object") != "whatsapp_business_account":
        return HttpResponse(status=200)

    backend = _get_whatsapp_backend()
    if not backend:
        logger.warning("WhatsApp webhook: IM_BACKEND is not WhatsAppBackend")
        return HttpResponse(status=200)

    from care_im.backends.whatsapp import get_webhook_value

    value = get_webhook_value(body)
    statuses = value.get("statuses")
    if statuses:
        _handle_status_update(statuses)

    if not value.get("messages"):
        return HttpResponse(status=200)

    try:
        msg = backend.receive_message(body)
        sender = (msg.sender or "").lstrip("+")
        logger.info(
            "WhatsApp webhook: received from %s: %s",
            sender,
            msg.content or "(no text)",
        )

        reply = get_care_reply(msg.content or "", sender=sender)

        if reply and sender:
            try:
                message_id = send_im_message(
                    content=reply["content"][:4096],
                    recipient=sender,
                    message_type=reply["message_type"],
                    metadata=reply.get("metadata"),
                    platform="whatsapp",
                    backend_instance=backend,
                    fail_silently=True,
                )
                if message_id:
                    logger.info("WhatsApp webhook: reply sent to %s (%s)", sender, message_id)
                else:
                    logger.warning(
                        "WhatsApp webhook: reply not sent (silent failure) to %s",
                        sender,
                    )
            except Exception:
                logger.exception("WhatsApp webhook: send failed")
    except Exception:
        logger.exception("WhatsApp webhook: handle message error")

    return HttpResponse(status=200)
