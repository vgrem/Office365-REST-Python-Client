from office365.sharepoint.base_entity import BaseEntity


class AppCollection(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.AppServices.AppCollection"
