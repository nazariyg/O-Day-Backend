import os

import django.db.models as m

from model_utils.models import TimeStampedModel

from .mixins import ItemMixin
from .videotag import VideoTag
from ..storages import OverwriteStorage


def get_upload_to(instance, filename):
    return os.path.join("videos", os.path.join(str(instance.item_id).zfill(5), filename))


class Video(ItemMixin, TimeStampedModel):

    VENDOR_CHOICES = [
        ("ab", "Artbeats"),
        ("cs", "CuteStockFootage"),
        ("dh", "Digital Hotcakes"),
        ("dv", "Digital Vision"),
        ("is", "iStock"),
        ("mm", "Mitch Martinez"),
        ("mv", "motionVFX"),
        ("pd", "Public Domain"),
        ("pf", "Photodisc Film"),
        ("uk", "Unknown"),
        ("v3", "Video3D"),
        ("vb", "VideoBlocks"),
        ("vc", "Video Copilot"),
    ]

    ASPECT_CHOICES = [
        ("3x4", "3x4"),
        ("9x16", "9x16"),
    ]

    OVERLAY_MODE_CHOICES = [
        ("sc", "Screen"),
        ("ov", "Overlay"),
        ("ld", "Linear Dodge"),
        ("mu", "Multiply"),
        ("lb", "Linear Burn"),
    ]

    SUB_ALIGN_CHOICES = [
        ("c", "Center"),
        ("b", "Bottom"),
        ("t", "Top"),
        ("l", "Left"),
        ("r", "Right"),
    ]

    TIME_ALIGN_CHOICES = [
        ("s", "Start"),
        ("e", "End"),
        ("m", "Middle"),
    ]

    item_id = m.IntegerField(unique=True, db_index=True)
    vendor = m.CharField(choices=VENDOR_CHOICES, max_length=2)
    orig_fn = m.CharField(max_length=250)
    aspect = m.CharField(choices=ASPECT_CHOICES, max_length=10)
    tags = m.ManyToManyField(VideoTag)

    native_loop = m.BooleanField(default=False)
    joint_time = m.FloatField(
        default=3.0)  # 2.0 for ic_light_glass_leaks, 1.0 for ic_light_leaks_fast
    sub_align = m.CharField(choices=SUB_ALIGN_CHOICES, max_length=1, default="c")
    time_align = m.CharField(choices=TIME_ALIGN_CHOICES, max_length=1, default="s")
    is_overlay = m.BooleanField(default=False)
    overlay_mode = m.CharField(
        choices=OVERLAY_MODE_CHOICES, max_length=2, default="sc")
    is_good = m.BooleanField(default=False)
    is_bad = m.BooleanField(default=False)
    only_3x4 = m.BooleanField(default=False)
    only_9x16 = m.BooleanField(default=False)
    has_sound = m.BooleanField(default=False)
    bitrate = m.FloatField(null=True, blank=True)
    length = m.FloatField(null=True, blank=True)
    is_hidden = m.BooleanField(default=False)
    num_uses = m.BigIntegerField(default=0)
    last_num_uses_modified_from_ip = m.GenericIPAddressField(default="", null=True)
    v_hd = m.FileField(upload_to=get_upload_to, storage=OverwriteStorage(), blank=True)
    v_sd = m.FileField(upload_to=get_upload_to, storage=OverwriteStorage(), blank=True)
    v_md = m.FileField(upload_to=get_upload_to, storage=OverwriteStorage(), blank=True)
    v_ld = m.FileField(upload_to=get_upload_to, storage=OverwriteStorage(), blank=True)
    t_hd = m.ImageField(upload_to=get_upload_to, storage=OverwriteStorage(), blank=True)
    t_sd = m.ImageField(upload_to=get_upload_to, storage=OverwriteStorage(), blank=True)
    t_md = m.ImageField(upload_to=get_upload_to, storage=OverwriteStorage(), blank=True)
    t_ld = m.ImageField(upload_to=get_upload_to, storage=OverwriteStorage(), blank=True)

    # def get_recc_def(self):
    #     return getattr(self, "recc_def", None)

    def get_hd_byte_size(self):
        return self.bitrate*1000000*self.length/8

    def get_is_sd_minimum(self):
        return "ic_static" in [tag.name for tag in self.tags.all()]

    def __str__(self):
        return "{} - {}".format(self.get_vendor_display(), self.orig_fn)
