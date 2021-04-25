from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.logger.logFileInfo import LogFileInfo


class LogFileInfoCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(LogFileInfoCollection, self).__init__(context, LogFileInfo, resource_path)
