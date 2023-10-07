from typing import TypeVar

from office365.runtime.client_object_collection import ClientObjectCollection

T = TypeVar("T")


class BaseEntityCollection(ClientObjectCollection[T]):
    """
    SharePoint entity set
    """

    @property
    def context(self):
        """
        :rtype: office365.sharepoint.client_context.ClientContext
        """
        return self._context
