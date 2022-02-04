from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.likes.user_entity import UserEntity


class LikedByInformation(BaseEntity):
    """Represents the information about the set of users who liked the list item."""

    @property
    def like_count(self):
        """
        Number of users that have liked the item.

        :rtype: int or None
        """
        return self.properties.get("LikeCount", None)

    @property
    def is_liked_by_user(self):
        """
        MUST be TRUE if the current user has liked the list item.

        :rtype: bool or None
        """
        return self.properties.get("isLikedByUser", None)

    @property
    def liked_by(self):
        """
        List of like entries corresponding to individual likes. MUST NOT contain more than one entry
        for the same user in the set.
        """
        return self.properties.get('likedBy', BaseEntityCollection(self.context, UserEntity,
                                                                   ResourcePath("likedBy", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "likedBy": self.liked_by,
            }
            default_value = property_mapping.get(name, None)
        return super(LikedByInformation, self).get_property(name, default_value)
