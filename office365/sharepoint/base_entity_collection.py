from office365.runtime.client_object_collection import ClientObjectCollection


class BaseEntityCollection(ClientObjectCollection):
    """Represents a collection of View resources."""

    def __init__(self, context, child_item_type=None, resource_path=None, parent=None):
        """
        SharePoint entity set

        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :type child_item_type: type[ClientObject]
        :type resource_path: office365.runtime.client_path.ClientPath
        :type parent: office365.sharepoint.base_entity.BaseEntity or None
        """
        super(BaseEntityCollection, self).__init__(context, child_item_type, resource_path)
        self._parent = parent
