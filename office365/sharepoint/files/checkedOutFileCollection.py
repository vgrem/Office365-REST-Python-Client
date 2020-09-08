from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.files.checkedOutFile import CheckedOutFile


class CheckedOutFileCollection(ClientObjectCollection):
    def __init__(self, context, resource_path=None):
        super(CheckedOutFileCollection, self).__init__(context, CheckedOutFile, resource_path)
