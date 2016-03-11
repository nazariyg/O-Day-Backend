import haystack.indexes as i

from .models import Video
from .models import Picture
from .settings import GOOD_PICTURE_INDEX_BOOST


class VideoIndex(i.SearchIndex, i.Indexable):

    text = i.MultiValueField(document=True)
    suggestions = i.FacetMultiValueField()

    def get_model(self):
        return Video

    def prepare_text(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def prepare(self, obj):
        # DYM (used for auto-correction).
        data = super(VideoIndex, self).prepare(obj)
        data["suggestions"] = data["text"]
        return data


class PictureIndex(i.SearchIndex, i.Indexable):

    text = i.MultiValueField(document=True)
    suggestions = i.FacetMultiValueField()

    def get_model(self):
        return Picture

    def prepare_text(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def prepare(self, obj):
        # DYM (used for auto-correction).
        data = super(PictureIndex, self).prepare(obj)
        data["suggestions"] = data["text"]

        # Promote good ones.
        if obj.is_good:
            data["boost"] = GOOD_PICTURE_INDEX_BOOST

        return data
