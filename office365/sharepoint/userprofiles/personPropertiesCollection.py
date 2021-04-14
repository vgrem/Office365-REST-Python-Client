from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.userprofiles.personProperties import PersonProperties


class PersonPropertiesCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(PersonPropertiesCollection, self).__init__(context, PersonProperties, resource_path)
