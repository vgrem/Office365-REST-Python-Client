from office365.outlookservices.item import Item


class Contact(Item):
    """User's contact."""

    @property
    def contact_id(self):
        if self.is_property_available('id'):
            return self.properties["id"]
        return None
