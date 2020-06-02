from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path import ResourcePath
from office365.graph.teams.channel import Channel


class ChannelCollection(ClientObjectCollection):
    """Team's collection"""

    def __init__(self, context, resource_path=None):
        super(ChannelCollection, self).__init__(context, Channel, resource_path)

    def __getitem__(self, key):
        if type(key) == int:
            return self._data[key]
        return Channel(self.context, ResourcePath(key, self.resource_path))
