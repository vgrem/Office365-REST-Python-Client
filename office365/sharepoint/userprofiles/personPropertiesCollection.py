from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.userprofiles.personProperties import PersonProperties


class PersonPropertiesCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(PersonPropertiesCollection, self).__init__(context, PersonProperties, resource_path)
