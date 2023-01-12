from office365.sharepoint.base_entity import BaseEntity


class MyGroupsResult(BaseEntity):

    @property
    def entity_type_name(self):
        return "SP.Directory.MyGroupsResult"
