from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.files.checkedOutFile import CheckedOutFile


class CheckedOutFileCollection(BaseEntityCollection):
    def __init__(self, context, resource_path=None):
        super(CheckedOutFileCollection, self).__init__(context, CheckedOutFile, resource_path)
