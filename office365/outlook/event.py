from office365.outlook.item import Item


class Event(Item):
    """An event in a calendar."""

    @property
    def id(self):
        return self.properties.get("id", None)
