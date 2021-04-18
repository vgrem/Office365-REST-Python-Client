from office365.entity_collection import EntityCollection
from office365.teams.channel import Channel


class ChannelCollection(EntityCollection):
    """Team's collection"""

    def __init__(self, context, resource_path=None):
        super(ChannelCollection, self).__init__(context, Channel, resource_path)

    def add(self, displayName, description=None):
        """Create a new channel in a Microsoft Team, as specified in the request body.

        :param str description: Optional textual description for the channel.
        :param str displayName: Channel name as it will appear to the user in Microsoft Teams.
        :rtype: Channel
        """
        payload = {
            "displayName": displayName,
            "description": description,
        }
        return self.add_from_json(payload)
