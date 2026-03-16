from __future__ import annotations

import json
from unittest.mock import patch

from django.test import RequestFactory, TestCase, override_settings

from care_im.views import whatsapp_webhook

WEBHOOK_URL = "/im/webhook/whatsapp/"
WEBHOOK_SETTINGS = {
    "IM_BACKEND": "care_im.backends.whatsapp.WhatsAppBackend",
    "WHATSAPP_PHONE_NUMBER_ID": "123456",
    "WHATSAPP_ACCESS_TOKEN": "test_token",
    "WHATSAPP_VERIFY_TOKEN": "test_verify",
}


def _whatsapp_message_payload(from_number="919876543210", text="hello"):
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "metadata": {"display_phone_number": "15550001234"},
                            "messages": [
                                {
                                    "from": from_number,
                                    "type": "text",
                                    "text": {"body": text},
                                }
                            ],
                        }
                    }
                ]
            }
        ],
    }


def _whatsapp_status_payload():
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "metadata": {"display_phone_number": "15550001234"},
                            "statuses": [
                                {
                                    "id": "wamid.abc123",
                                    "status": "delivered",
                                    "recipient_id": "919876543210",
                                }
                            ],
                        }
                    }
                ]
            }
        ],
    }


@override_settings(**WEBHOOK_SETTINGS)
class TestWhatsAppWebhookVerification(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_valid_token_returns_challenge(self):
        request = self.factory.get(
            WEBHOOK_URL,
            {
                "hub.mode": "subscribe",
                "hub.verify_token": "test_verify",
                "hub.challenge": "challenge_abc",
            },
        )
        response = whatsapp_webhook(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "challenge_abc")

    def test_invalid_token_returns_403(self):
        request = self.factory.get(
            WEBHOOK_URL,
            {
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong_token",
                "hub.challenge": "challenge_abc",
            },
        )
        response = whatsapp_webhook(request)
        self.assertEqual(response.status_code, 403)


@override_settings(**WEBHOOK_SETTINGS)
class TestWhatsAppWebhookPost(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _post(self, data):
        body = json.dumps(data) if isinstance(data, dict) else data
        request = self.factory.post(WEBHOOK_URL, data=body, content_type="application/json")
        return whatsapp_webhook(request)

    @patch("care_im.views.send_im_message")
    @patch("care_im.backends.whatsapp.WhatsAppBackend._get_client")
    def test_incoming_message_triggers_reply(self, mock_client, mock_send):
        mock_send.return_value = "wamid.reply"
        response = self._post(_whatsapp_message_payload(text="hi"))
        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args.kwargs["recipient"], "919876543210")

    def test_status_update_returns_200(self):
        response = self._post(_whatsapp_status_payload())
        self.assertEqual(response.status_code, 200)

    def test_invalid_json_returns_200(self):
        response = self._post("not json")
        self.assertEqual(response.status_code, 200)

    def test_non_whatsapp_object_returns_200(self):
        response = self._post({"object": "page", "entry": []})
        self.assertEqual(response.status_code, 200)
