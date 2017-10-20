from office365.runtime.client_object import ClientObject
from office365.runtime.odata.odata_path_parser import ODataPathParser
from office365.runtime.resource_path_entry import ResourcePathEntry
from office365.sharepoint.file import AbstractFile


class Attachmentfile(AbstractFile):
    """Represents an attachment file in a SharePoint List Item."""

    @property
    def resource_path(self):
        orig_path = ClientObject.resource_path.fget(self)
        if self.is_property_available("ServerRelativeUrl") and orig_path is None:
            return ResourcePathEntry(self.context,
                                     self.context.web.resource_path,
                                     ODataPathParser.from_method("GetFileByServerRelativeUrl",
                                                                 [self.properties["ServerRelativeUrl"]]))
        return orig_path
