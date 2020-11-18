from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.logger.logFileInfo import LogFileInfo


class LogFileInfoCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(LogFileInfoCollection, self).__init__(context, LogFileInfo, resource_path)
