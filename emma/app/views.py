import re
import random
import os
import json

from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.exceptions import NotAuthenticated, ValidationError, PermissionDenied
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery

from .models import Video
from .models import Picture
from .serializers import VideoSerializerInput, VideoSerializerOutput
from .serializers import PictureSerializerInput, PictureSerializerOutput
from .settings import BOOST_SEARCH_RESULTS_ON_NUM_USES
from .settings import BOOST_SEARCH_RESULTS_WEIGHT_POS, BOOST_SEARCH_RESULTS_WEIGHT_USES
from .settings import NUM_USES_INCREMENT_TIME_BARRIER_GENERAL
from .settings import NUM_USES_INCREMENT_TIME_BARRIER_SAME_IP
from .utils import get_bool_query_str_param, get_request_ip

from django.http import JsonResponse


def validate_request_on_app_id(request):
    if "app" in request.query_params:
        app_id = request.query_params["app"]
        known_app_ids = [
            "Omitted."
        ]
        if app_id not in known_app_ids:
            raise ValidationError("")
    else:
        raise ValidationError("")


def boost_search_results_on_num_uses(items):
    if not items:
        return items
    item_class = items[0].__class__

    weight_pos = BOOST_SEARCH_RESULTS_WEIGHT_POS
    weight_uses = BOOST_SEARCH_RESULTS_WEIGHT_USES
    weight_sum = weight_pos + weight_uses
    max_num_uses = item_class.objects.aggregate(Max("num_uses"))["num_uses__max"]
    num_items = len(items)
    for i, item in enumerate(items):
        rating_pos = (num_items - i)/num_items
        rating_uses = item.num_uses/(max_num_uses + 1)
        item.rating = (rating_pos*weight_pos + rating_uses*weight_uses)/weight_sum
    items.sort(key=lambda item: item.rating, reverse=True)

    return items


def get_item_and_maybe_increment_num_uses(view):
    queryset = view.get_queryset()
    item = get_object_or_404(queryset, item_id=view.kwargs[view.lookup_field])

    if "iu" in view.request.query_params:
        do_update = False
        time_diff = timezone.now() - item.modified
        if time_diff.seconds > NUM_USES_INCREMENT_TIME_BARRIER_GENERAL:
            user_ip = get_request_ip(view.request)
            if (user_ip != item.last_num_uses_modified_from_ip or
                time_diff.seconds > NUM_USES_INCREMENT_TIME_BARRIER_SAME_IP):
                do_update = True
        if do_update:
            item.num_uses += 1
            item.last_num_uses_modified_from_ip = user_ip
            item.save()

    return item


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_root(request):
    return Response({
            "videos": reverse("video-list", request=request),
            "pictures": reverse("picture-list", request=request)
        })


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Videos.


class VideoListCreateView(generics.ListCreateAPIView):

    http_method_names = ["get", "post", "head"]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return VideoSerializerOutput
        else:
            return VideoSerializerInput

    def get_queryset(self):
        if self.request.method in SAFE_METHODS:
            # Listing/searching.

            # Query string parameters.
            validate_request_on_app_id(self.request)
            if "q" in self.request.query_params:
                search_q = self.request.query_params["q"]
            else:
                # No query is provided. Full list is for authenticated requests only.
                if self.request.user.is_authenticated():
                    return Video.objects.order_by("item_id")
                else:
                    raise NotAuthenticated("")
            if "a" in self.request.query_params:
                aspect = self.request.query_params["a"]
                if aspect not in ["3x4", "9x16"]:
                    raise ValidationError("")
            else:
                raise ValidationError("")

            search_q = search_q.strip()
            search_q = search_q.lower()
            search_q = re.sub(r"\s+", " ", search_q)

            if re.search(r"\w-(?!ic_\w+)", search_q) is not None:
                search_q = search_q.replace("-", " ")
            search_q = search_q.replace(".", "")
            search_q = search_q.replace("'", "")
            search_q = search_q.strip()

            # Prevent responding with full list if the search query is empty.
            if not search_q:
                return Video.objects.none()

            sqs = SearchQuerySet().models(Video)

            query_is_categorical = False

            ic_pattern = r"^([=\-]ic_\w+)+$"
            if re.search(ic_pattern, search_q) is None:
                # A regular search query.

                sqs = sqs.filter(content=AutoQuery(search_q))
                videos = [sr.object for sr in sqs.load_all()]

            else:
                # Category or categories, e.g. =ic_categ=ic_categ-ic_categ

                query_is_categorical = True

                qs = Video.objects.all()
                qs_methods = {
                    "=": "filter",
                    "-": "exclude",
                }
                feed = search_q
                while True:
                    m = re.search(r"^(.+?)\b(ic_\w+)", feed)
                    if m is None:
                        break
                    feed = feed[m.end():]
                    qs = getattr(qs, qs_methods[m.group(1)])(tags__name=m.group(2))
                videos = list(qs)

            if not videos and not query_is_categorical:
                # Auto-correction.
                sugg = sqs.spelling_suggestion()
                if (sugg is not None) and ("suggestion" in sugg) and sugg["suggestion"]:
                    sqs = SearchQuerySet().models(Video)
                    sqs = sqs.filter(content=sugg["suggestion"][0])
                    videos = [sr.object for sr in sqs.load_all()]

            # Exclude hidden.
            videos = [video for video in videos if not video.is_hidden]

            # Exclude by aspect restrictions.
            if aspect == "3x4":
                videos = [video for video in videos if not video.only_9x16]
            else:  # 9x16
                videos = [video for video in videos if not video.only_3x4]

            if "o" in self.request.query_params:
                # Exclude by overlay.
                overlay_only = get_bool_query_str_param(self.request.query_params["o"])
                if overlay_only:
                    # Overlay only.
                    videos = [video for video in videos if video.is_overlay]
                else:
                    # Non-overlay only.
                    videos = [video for video in videos if not video.is_overlay]

            # Sort on good/bad with local randomization.
            videos_good = [video for video in videos if video.is_good and not video.is_bad]
            videos_other = [video for video in videos if not video.is_good and not video.is_bad]
            videos_bad = [video for video in videos if video.is_bad and not video.is_good]
            random.shuffle(videos_good)
            random.shuffle(videos_other)
            random.shuffle(videos_bad)

            # Join.
            videos = videos_good + videos_other# + videos_bad

            if BOOST_SEARCH_RESULTS_ON_NUM_USES:
                videos = boost_search_results_on_num_uses(videos)

            return videos

        else:
            return Video.objects.all()


class VideoRetrieveUpdateView(generics.RetrieveUpdateAPIView):

    http_method_names = ["get", "put", "head"]
    queryset = Video.objects.all()
    lookup_field = "item_id"

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return VideoSerializerOutput
        else:
            return VideoSerializerInput

    def get_object(self):
        return get_item_and_maybe_increment_num_uses(self)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Pictures.


class PictureListCreateView(generics.ListCreateAPIView):

    http_method_names = ["get", "post", "head"]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return PictureSerializerOutput
        else:
            return PictureSerializerInput

    def get_queryset(self):
        if self.request.method in SAFE_METHODS:
            # Listing/searching.

            validate_request_on_app_id(self.request)
            if "q" in self.request.query_params:
                search_q = self.request.query_params["q"]
            else:
                # No query is provided. Full list is for authenticated requests only.
                if not self.request.user.is_authenticated():
                    raise NotAuthenticated("")
                return Picture.objects.order_by("item_id")

            search_q = search_q.strip()
            search_q = search_q.lower()
            search_q = re.sub(r"\s+", " ", search_q)

            search_q = search_q.replace("-", " ")
            search_q = search_q.replace(".", "")
            search_q = search_q.replace("'", "")
            search_q = search_q.strip()

            if not search_q:
                return Picture.objects.none()

            sqs = SearchQuerySet().models(Picture)
            sqs = sqs.filter(content=AutoQuery(search_q))

            pictures = [sr.object for sr in sqs.load_all()]

            if not pictures:
                # Auto-correction.
                sugg = sqs.spelling_suggestion()
                if (sugg is not None) and ("suggestion" in sugg) and sugg["suggestion"]:
                    sqs = SearchQuerySet().models(Picture)
                    sqs = sqs.filter(content=sugg["suggestion"][0])
                    pictures = [sr.object for sr in sqs.load_all()]

            # Exclude hidden.
            pictures = [picture for picture in pictures if not picture.is_hidden]

            # Randomize leading good ones.
            first_non_good_picture_pos = None
            for i, picture in enumerate(pictures):
                if not picture.is_good:
                    first_non_good_picture_pos = i
                    break
            if first_non_good_picture_pos is not None:
                leading_good_pictures = pictures[:first_non_good_picture_pos]
                random.shuffle(leading_good_pictures)
                pictures = leading_good_pictures + pictures[first_non_good_picture_pos:]

            if BOOST_SEARCH_RESULTS_ON_NUM_USES:
                pictures = boost_search_results_on_num_uses(pictures)

            return pictures

        else:
            return Picture.objects.all()


class PictureRetrieveUpdateView(generics.RetrieveUpdateAPIView):

    http_method_names = ["get", "put", "head"]
    queryset = Picture.objects.all()
    lookup_field = "item_id"

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return PictureSerializerOutput
        else:
            return PictureSerializerInput

    def get_object(self):
        return get_item_and_maybe_increment_num_uses(self)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def appSuperConfig(request):
    config = {}

    config["vPreviewPhoneWiFiHDDownloadSecondsHDBitrateRes0"] = "md"  # reflected

    return JsonResponse(config)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
