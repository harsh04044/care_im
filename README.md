# care_im — IM plugin for CARE

Proof-of-concept plugin that adds instant messaging support to
[CARE](https://github.com/ohcnetwork/care), mirroring its existing SMS
backend style. Built as a GSoC 2025 mini-PoC.

## Architecture

```
 WhatsApp / Telegram / …
        │
        ▼
 ┌─────────────┐      ┌──────────────┐      ┌──────────────┐
 │  Webhook     │─────▶│  IMBackend   │─────▶│  IMMessage   │
 │  (views.py)  │      │  (whatsapp,  │      │  (message.py)│
 │              │◀─────│   console)   │◀─────│              │
 └─────────────┘      └──────────────┘      └──────────────┘
        │                                          │
        ▼                                          ▼
 ┌─────────────┐                           ┌──────────────┐
 │  care_poc.py │                           │  utils.py    │
 │  (CARE bot   │                           │  (send_im_   │
 │   logic)     │                           │   message)   │
 └─────────────┘                           └──────────────┘
```

## Features

- Backends: `ConsoleIMBackend` (dev/tests), `WhatsAppBackend` (Cloud API)
- WhatsApp interactive messages (buttons + list) for the PoC flow
- Send + receive on every backend (`send_message()`, `receive_message()`)
- 1:1 conversations (recipient is a single string, not a list)
- Simple conversation state: welcome → category → patient → data (in this PoC, state is in-memory; in production this would use Redis, which CARE already has)
- Django app: add to `INSTALLED_APPS`

## How this maps to real CARE

This PoC uses mock data and in-memory state to demonstrate the flow. In a real deployment: the mock patient/medication/procedure data would come from CARE's actual `Patient` and related models; the in-memory conversation state would be replaced by Redis (already used in CARE); and the console backend would be swapped for the WhatsApp backend with real Meta credentials.

## Quick Start

### Standalone (demo site)

```bash
# Clone and install
git clone <repo-url> && cd care_im
pip install -e ".[dev]"

# Set up WhatsApp credentials
cp .env.example .env   # edit with your Meta API credentials

# Run the demo server
python manage_demo.py runserver
```

### As a CARE plugin

```python
# settings.py
INSTALLED_APPS = [..., "care_im"]
IM_BACKEND = "care_im.backends.whatsapp.WhatsAppBackend"
WHATSAPP_PHONE_NUMBER_ID = "your_phone_number_id"
WHATSAPP_ACCESS_TOKEN = "your_access_token"
WHATSAPP_VERIFY_TOKEN = "your_verify_token"
```

```python
# urls.py
urlpatterns = [
    path("im/", include("care_im.urls")),
]
```

### Sending a message programmatically

```python
from care_im.utils import send_im_message

send_im_message(content="Hello!", recipient="919876543210")
```

## Running Tests

```bash
python -m django test care_im.tests --settings=test_settings -v2
```

## Code Quality

```bash
# Lint
ruff check care_im/

# Format
ruff format care_im/

# Pre-commit (install once)
pre-commit install
```

## Project Structure

```
care_im/
├── __init__.py              # Package exports
├── apps.py                  # Django AppConfig
├── message.py               # IMMessage model
├── utils.py                 # send_im_message(), get_im_backend()
├── views.py                 # Webhook endpoints
├── urls.py                  # URL routing
├── care_poc.py              # Interactive CARE bot (PoC)
├── backends/
│   ├── base.py              # IMBackendBase (abstract)
│   ├── console.py           # ConsoleIMBackend (dev/test)
│   └── whatsapp.py          # WhatsAppBackend (Cloud API)
└── tests/
    └── test_views.py        # Webhook endpoint tests
```
