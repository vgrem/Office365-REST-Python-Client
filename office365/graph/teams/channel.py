from office365.graph.entity import Entity


class Channel(Entity):
    """Teams are made up of channels, which are the conversations you have with your teammates"""

    @property
    def web_url(self):
        """A hyperlink that will navigate to the channel in Microsoft Teams. This is the URL that you get when you
        right-click a channel in Microsoft Teams and select Get link to channel. This URL should be treated as an
        opaque blob, and not parsed. Read-only.

        :rtype: str or None """
        return self.properties.get('webUrl', None)
