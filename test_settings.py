SECRET_KEY = "test-secret-key"
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "care_im",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
IM_BACKEND = "care_im.backends.console.ConsoleIMBackend"
