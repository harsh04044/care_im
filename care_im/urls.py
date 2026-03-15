from django.http import HttpResponse
from django.urls import path

from care_im.views import whatsapp_webhook


def webhook_placeholder(request, platform):
    return HttpResponse(status=200)


urlpatterns = [
    path("webhook/whatsapp/", whatsapp_webhook, name="im_webhook_whatsapp"),
    path("webhook/<str:platform>/", webhook_placeholder, name="im_webhook"),
]
