class ItemMixin():

    def get_tags(self):
        return [tag.name for tag in self.tags.all()]
