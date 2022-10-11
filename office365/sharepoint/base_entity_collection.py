from office365.runtime.client_object_collection import ClientObjectCollection


class BaseEntityCollection(ClientObjectCollection):

    @property
    def context(self):
        """
        :rtype: office365.sharepoint.client_context.ClientContext
        """
        return self._context
