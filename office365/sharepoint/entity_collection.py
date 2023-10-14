from typing import TYPE_CHECKING, TypeVar

from office365.runtime.client_object_collection import ClientObjectCollection

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext

T = TypeVar("T")


class EntityCollection(ClientObjectCollection[T]):
    """
    SharePoint's entity set
    """

    @property
    def context(self):
        # type: () -> ClientContext
        return self._context
