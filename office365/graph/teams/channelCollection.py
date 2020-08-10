from office365.graph.teams.channel import Channel
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import CreateEntityQuery
from office365.runtime.resource_path import ResourcePath


class ChannelCollection(ClientObjectCollection):
    """Team's collection"""

    def __init__(self, context, resource_path=None):
        super(ChannelCollection, self).__init__(context, Channel, resource_path)

    def __getitem__(self, key):
        if type(key) == int:
            return self._data[key]
        return Channel(self.context, ResourcePath(key, self.resource_path))

    def add(self, displayName, description=None):
        """Create a new channel in a Microsoft Team, as specified in the request body.

        :param str description: Optional textual description for the channel.
        :param str displayName: Channel name as it will appear to the user in Microsoft Teams.
        """
        new_channel = Channel(self.context)
        payload = {
            "displayName": displayName,
            "description": description,
        }
        qry = CreateEntityQuery(self, payload, new_channel)
        self.context.add_query(qry)
        return new_channel
