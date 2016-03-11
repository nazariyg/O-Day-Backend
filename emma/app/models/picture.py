import os

import django.db.models as m

from model_utils.models import TimeStampedModel

from .mixins import ItemMixin
from .picturetag import PictureTag
from ..storages import OverwriteStorage


def get_upload_to(instance, filename):
    return os.path.join("pictures", os.path.join(str(instance.item_id).zfill(5), filename))


class Picture(ItemMixin, TimeStampedModel):

    VENDOR_CHOICES = [
        ("ss", "Shutterstock"),
        ("ft", "Fotolia"),
        ("ws", "Webshots"),
        ("dt", "Dreamstime"),
        ("ps", "Photoshop Stock Art"),
        ("ot", "Other"),
    ]

    ASPECT_CHOICES = [
        ("3x4", "3x4"),
        ("9x16", "9x16"),
    ]

    SUB_ALIGN_CHOICES = [
        ("c", "Center"),
        ("b", "Bottom"),
        ("t", "Top"),
        ("l", "Left"),
        ("r", "Right"),
    ]

    item_id = m.IntegerField(unique=True, db_index=True)
    vendor = m.CharField(choices=VENDOR_CHOICES, max_length=2)
    orig_fn = m.CharField(max_length=250)
    aspect = m.CharField(choices=ASPECT_CHOICES, max_length=10)
    tags = m.ManyToManyField(PictureTag)

    sub_align = m.CharField(choices=SUB_ALIGN_CHOICES, max_length=1, default="c")
    is_good = m.BooleanField(default=False)
    is_hidden = m.BooleanField(default=False)
    num_uses = m.BigIntegerField(default=0)
    last_num_uses_modified_from_ip = m.GenericIPAddressField(default="", null=True)
    p_hd = m.ImageField(upload_to=get_upload_to, storage=OverwriteStorage(), blank=True)
    p_sd = m.ImageField(upload_to=get_upload_to, storage=OverwriteStorage(), blank=True)
    p_md = m.ImageField(upload_to=get_upload_to, storage=OverwriteStorage(), blank=True)
    p_ld = m.ImageField(upload_to=get_upload_to, storage=OverwriteStorage(), blank=True)

    def __str__(self):
        return "{} - {}".format(self.get_vendor_display(), self.orig_fn)
