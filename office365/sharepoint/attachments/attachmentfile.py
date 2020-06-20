from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.files.file import AbstractFile


class AttachmentFile(AbstractFile):
    """Represents an attachment file in a SharePoint List Item."""

    def set_property(self, name, value, persist_changes=True):
        super(AttachmentFile, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "ServerRelativeUrl":
            self._resource_path = ResourcePathServiceOperation(
                "GetFileByServerRelativeUrl", [value], ResourcePath("Web"))
