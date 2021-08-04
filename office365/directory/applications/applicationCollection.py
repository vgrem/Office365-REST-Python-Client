from office365.directory.applications.application import Application
from office365.entity_collection import EntityCollection


class ApplicationCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(ApplicationCollection, self).__init__(context, Application, resource_path)

    def add(self, display_name):
        """
        Create a new application object.
        :type display_name: str
        """
        return super(ApplicationCollection, self).add(displayName=display_name)
