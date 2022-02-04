from office365.sharepoint.base_entity import BaseEntity


class UserEntity(BaseEntity):
    """Represents a single like within a likedBy set of the list item."""

    @property
    def creation_date(self):
        """
        The Datetime of the like.
        """
        return self.properties.get("creationDate", None)
