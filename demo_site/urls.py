from django.urls import include, path

urlpatterns = [
    path("im/", include("care_im.urls")),
]
