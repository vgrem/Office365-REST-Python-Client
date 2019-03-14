from office365.outlookservices.item import Item


class Contact(Item):
    """User's contact."""

    @property
    def contact_id(self):
        if self.is_property_available('Id'):
            return self.properties["Id"]
        return None
