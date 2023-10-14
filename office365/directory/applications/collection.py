from office365.delta_collection import DeltaCollection
from office365.directory.applications.application import Application
from office365.runtime.paths.appid import AppIdPath


class ApplicationCollection(DeltaCollection[Application]):
    """DirectoryObject's collection"""

    def __init__(self, context, resource_path=None):
        super(ApplicationCollection, self).__init__(context, Application, resource_path)

    def get_by_app_id(self, app_id):
        # type: (str) -> Application
        """Retrieves application by Application client identifier

        :param str app_id: Application client identifier
        """
        return Application(self.context, AppIdPath(app_id, self.resource_path))
