from office365.sharepoint.base_entity import BaseEntity


class UserEntity(BaseEntity):
    """Represents a single like within a likedBy set of the list item."""

    @property
    def creation_date(self):
        """
        The Datetime of the like.
        """
        return self.properties.get("creationDate", None)

    @property
    def email(self):
        """
        The email of the user who liked the item.

        :rtype: str
        """
        return self.properties.get("email", None)
