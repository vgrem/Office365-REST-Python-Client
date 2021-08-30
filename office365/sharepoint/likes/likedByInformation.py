from office365.sharepoint.base_entity import BaseEntity


class LikedByInformation(BaseEntity):

    @property
    def like_count(self):
        return self.properties.get("LikeCount", None)

    def set_property(self, name, value, persist_changes=True):
        super(LikedByInformation, self).set_property(name, value, persist_changes)
        return self


