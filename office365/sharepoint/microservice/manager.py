from office365.sharepoint.base_entity import BaseEntity


class MicroServiceManager(BaseEntity):

    @property
    def entity_type_name(self):
        return "SP.MicroService.MicroServiceManager"
