from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r"^api/$",
        views.api_root),

    url(r"^api/auth/",
        include("rest_framework.urls", namespace="rest_framework")),

    url(r"^api/videos/$",
        views.VideoListCreateView.as_view(),
        name="video-list"),
    url(r"^api/videos/(?P<item_id>\d+)/$",
        views.VideoRetrieveUpdateView.as_view(),
        name="video-detail"),

    url(r"^api/pictures/$",
        views.PictureListCreateView.as_view(),
        name="picture-list"),
    url(r"^api/pictures/(?P<item_id>\d+)/$",
        views.PictureRetrieveUpdateView.as_view(),
        name="picture-detail"),

    url(r"^c$",
        views.appSuperConfig),
]
