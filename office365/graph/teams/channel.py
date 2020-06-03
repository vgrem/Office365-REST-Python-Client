from office365.graph.entity import Entity


class Channel(Entity):
    """Teams are made up of channels, which are the conversations you have with your teammates"""

    @property
    def webUrl(self):
        """A hyperlink that will navigate to the channel in Microsoft Teams. This is the URL that you get when you
        right-click a channel in Microsoft Teams and select Get link to channel. This URL should be treated as an
        opaque blob, and not parsed. Read-only. """
        if self.is_property_available('webUrl'):
            return self.properties['webUrl']
        else:
            return None
