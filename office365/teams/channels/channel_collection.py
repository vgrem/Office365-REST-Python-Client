from office365.entity_collection import EntityCollection
from office365.teams.channels.channel import Channel


class ChannelCollection(EntityCollection):
    """Team's collection"""

    def __init__(self, context, resource_path=None):
        super(ChannelCollection, self).__init__(context, Channel, resource_path)

    def add(self, display_name, description=None):
        """Create a new channel in a Microsoft Team, as specified in the request body.

        :param str description: Optional textual description for the channel.
        :param str display_name: Channel name as it will appear to the user in Microsoft Teams.
        :rtype: Channel
        """
        return super(ChannelCollection, self).add(
            displayName=display_name,
            description=description
        )
