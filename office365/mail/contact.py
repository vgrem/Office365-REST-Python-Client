from office365.mail.item import Item


class Contact(Item):
    """User's contact."""

    @property
    def id(self):
        return self.properties.get("id", None)
