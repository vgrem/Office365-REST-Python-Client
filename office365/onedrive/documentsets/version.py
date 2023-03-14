from office365.directory.permissions.identity_set import IdentitySet
from office365.onedrive.documentsets.version_item import DocumentSetVersionItem
from office365.onedrive.versions.list_item import ListItemVersion
from office365.runtime.client_value_collection import ClientValueCollection


class DocumentSetVersion(ListItemVersion):
    """Represents the version of a document set item in a list."""

    @property
    def comment(self):
        """Comment about the captured version."""
        return self.properties.get("comment", None)

    @property
    def created_by(self):
        """User who captured the version."""
        return self.properties.get("createdBy", IdentitySet())

    @property
    def items(self):
        """Items within the document set that are captured as part of this version."""
        return self.properties.get("items", ClientValueCollection(DocumentSetVersionItem))

    @property
    def should_capture_minor_version(self):
        """
        If true, minor versions of items are also captured; otherwise, only major versions will be captured.
        Default value is false.
        """
        return self.properties.get("shouldCaptureMinorVersion", None)
