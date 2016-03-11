from django.contrib import admin

from .models import Video
from .models import VideoTag
from .models import Picture
from .models import PictureTag


admin.site.register(Video)
admin.site.register(VideoTag)
admin.site.register(Picture)
admin.site.register(PictureTag)
