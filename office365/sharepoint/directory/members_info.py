from office365.sharepoint.base_entity import BaseEntity


class MembersInfo(BaseEntity):

    @property
    def entity_type_name(self):
        return "SP.Directory.MembersInfo"
