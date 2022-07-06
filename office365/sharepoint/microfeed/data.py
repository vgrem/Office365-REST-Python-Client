from office365.sharepoint.base_entity import BaseEntity


class MicrofeedData(BaseEntity):

    @property
    def entity_type_name(self):
        return "SP.Microfeed.MicrofeedData"
