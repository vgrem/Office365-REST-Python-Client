from office365.onedrive.versions.base_item_version import BaseItemVersion
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


class DriveItemVersion(BaseItemVersion):
    """The DriveItemVersion resource represents a specific version of a DriveItem."""

    def restore_version(self):
        qry = ServiceOperationQuery(self, "restoreVersion")
        self.context.add_query(qry)
        return self

    @property
    def content(self):
        """
        The content stream for this version of the item.

        :rtype: str or bytes
        """
        return self.properties.get('content', None)

    @property
    def size(self):
        """
        Indicates the size of the content stream for this version of the item.

        :rtype: int
        """
        return self.properties.get('size', None)
