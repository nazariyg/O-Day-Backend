from django.core.exceptions import FieldDoesNotExist

import rest_framework.serializers as s

from .models import Video
from .models import VideoTag
from .models import Picture
from .models import PictureTag


class VideoSerializerInput(s.ModelSerializer):

    tags = s.ListField(child=s.CharField(max_length=250))

    class Meta:

        model = Video
        fields = [
            "item_id",
            "vendor",
            "orig_fn",
            "aspect",
            "tags",
            "native_loop",
            "joint_time",
            "sub_align",
            "time_align",
            "is_overlay",
            "overlay_mode",
            "is_good",
            "is_bad",
            "only_3x4",
            "only_9x16",
            "has_sound",
            "bitrate",
            "length",
            "is_hidden",
            "v_hd",
            "v_sd",
            "v_md",
            "v_ld",
            "t_hd",
            "t_sd",
            "t_md",
            "t_ld",
        ]

    def create(self, validated_data):
        data = dict(validated_data)

        tags_s = data["tags"]
        del data["tags"]

        if "ic_light_glass_leaks" in tags_s:
            data.setdefault("joint_time", 2.0)
        elif "ic_light_leaks_fast" in tags_s:
            data.setdefault("joint_time", 1.0)

        video = Video.objects.create(**data)

        tags = []
        for tag_s in tags_s:
            tag, created = VideoTag.objects.get_or_create(name=tag_s)
            tags.append(tag)
        video.tags = tags
        video.save()

        return video

    def update(self, instance, validated_data):
        data = dict(validated_data)
        data_has_tags = "tags" in data

        if data_has_tags:
            tags_s = data["tags"]
            del data["tags"]
            if "ic_light_glass_leaks" in tags_s:
                data.setdefault("joint_time", 2.0)
            elif "ic_light_leaks_fast" in tags_s:
                data.setdefault("joint_time", 1.0)

        for attr_s in data:
            try:
                Video._meta.get_field(attr_s)
                setattr(instance, attr_s, data[attr_s])
            except FieldDoesNotExist:
                pass
        instance.save()

        if data_has_tags:
            tags = []
            for tag_s in tags_s:
                tag, created = VideoTag.objects.get_or_create(name=tag_s)
                tags.append(tag)
            instance.tags = tags
            instance.save()

        return instance

    def to_representation(self, obj):
        return VideoSerializerOutput(obj, context=self.context).data


class VideoSerializerOutput(s.ModelSerializer):

    hd_bitrate = s.FloatField(source="bitrate")
    hd_byte_size = s.FloatField(source="get_hd_byte_size")
    is_sd_minimum = s.BooleanField(source="get_is_sd_minimum")

    class Meta:

        model = Video
        fields = [
            "item_id",
            "aspect",
            "native_loop",
            "joint_time",
            "sub_align",
            "time_align",
            "is_overlay",
            "overlay_mode",
            "is_good",
            "hd_bitrate",
            "hd_byte_size",
            "has_sound",
            "is_sd_minimum",
            "v_hd",
            "v_sd",
            "v_md",
            "v_ld",
            "t_hd",
            "t_sd",
            "t_md",
            "t_ld",
        ]


class PictureSerializerInput(s.ModelSerializer):

    tags = s.ListField(child=s.CharField(max_length=250))

    class Meta:

        model = Picture
        fields = [
            "item_id",
            "vendor",
            "orig_fn",
            "aspect",
            "tags",
            "sub_align",
            "is_good",
            "is_hidden",
            "p_hd",
            "p_sd",
            "p_md",
            "p_ld",
        ]

    def create(self, validated_data):
        data = dict(validated_data)

        tags_s = data["tags"]
        del data["tags"]

        picture = Picture.objects.create(**data)

        tags = []
        for tag_s in tags_s:
            tag, created = PictureTag.objects.get_or_create(name=tag_s)
            tags.append(tag)
        picture.tags = tags
        picture.save()

        return picture

    def update(self, instance, validated_data):
        data = dict(validated_data)
        data_has_tags = "tags" in data

        if data_has_tags:
            tags_s = data["tags"]
            del data["tags"]

        for attr_s in data:
            try:
                Picture._meta.get_field(attr_s)
                setattr(instance, attr_s, data[attr_s])
            except FieldDoesNotExist:
                pass
        instance.save()

        if data_has_tags:
            tags = []
            for tag_s in tags_s:
                tag, created = PictureTag.objects.get_or_create(name=tag_s)
                tags.append(tag)
            instance.tags = tags
            instance.save()

        return instance

    def to_representation(self, obj):
        return PictureSerializerOutput(obj, context=self.context).data


class PictureSerializerOutput(s.ModelSerializer):

    class Meta:

        model = Picture
        fields = [
            "item_id",
            "aspect",
            "sub_align",
            "p_hd",
            "p_sd",
            "p_md",
            "p_ld",
        ]
