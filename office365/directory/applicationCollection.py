from office365.directory.application import Application
from office365.entity_collection import EntityCollection


class ApplicationCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(ApplicationCollection, self).__init__(context, Application, resource_path)

    def add(self, displayName):
        """
        Create a new application object.
        :type displayName: str
        """
        return self.add_from_json({"displayName": displayName})
