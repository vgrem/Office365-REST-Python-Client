from office365.runtime.client_object_collection import ClientObjectCollection


class BaseEntityCollection(ClientObjectCollection):

    def __init__(self, context, item_type=None, resource_path=None, parent=None):
        """
        Represents a collection of SharePoint entities.

        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :type item_type: type[ClientObject]
        :type resource_path: office365.runtime.paths.resource_path.ResourcePath
        :type parent: office365.sharepoint.base_entity.BaseEntity or None
        """
        super(BaseEntityCollection, self).__init__(context, item_type, resource_path)
        self._parent = parent

    @property
    def parent(self):
        return self._parent
