from office365.runtime.odata.odata_path_parser import ODataPathParser
from office365.runtime.resource_path_entity import ResourcePathEntity
from office365.sharepoint.file import AbstractFile


class AttachmentFile(AbstractFile):
    """Represents an attachment file in a SharePoint List Item."""

    def set_property(self, name, value, serializable=True):
        super(AttachmentFile, self).set_property(name, value, serializable)
        # fallback: create a new resource path
        if name == "ServerRelativeUrl":
            self._resource_path = ResourcePathEntity(
                self.context,
                ResourcePathEntity(self.context, None, "Web"),
                ODataPathParser.from_method("GetFileByServerRelativeUrl", [value]))
