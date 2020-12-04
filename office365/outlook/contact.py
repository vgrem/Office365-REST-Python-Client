from office365.outlook.item import Item


class Contact(Item):
    """User's contact."""

    @property
    def id(self):
        if self.is_property_available('id'):
            return self.properties["id"]
        return None
