from office365.mail.item import Item


class Event(Item):
    """An event in a calendar."""

    @property
    def id(self):
        return self.properties.get("id", None)
