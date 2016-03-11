import django.db.models as m


class VideoTag(m.Model):

    name = m.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name
