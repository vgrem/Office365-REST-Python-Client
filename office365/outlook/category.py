from office365.entity import Entity


class OutlookCategory(Entity):
    """Represents a category by which a user can group Outlook items such as messages and events.
    The user defines categories in a master list, and can apply one or more
    of these user-defined categories to an item."""

    @property
    def color(self):
        """A pre-set color constant that characterizes a category, and that is mapped to one of 25 predefined colors"""
        return self.properties.get("color", None)

    @property
    def display_name(self):
        """A unique name that identifies a category in the user's mailbox.
        After a category is created, the name cannot be changed"""
        return self.properties.get("displayName", None)
