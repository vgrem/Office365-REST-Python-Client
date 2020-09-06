from office365.runtime.client_object_collection import ClientObjectCollection


class EntityCollection(ClientObjectCollection):

    @property
    def context(self):
        """
        :rtype: office365.graph_client.GraphClient
        """
        return self._context
