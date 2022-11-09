from office365.sharepoint.base_entity import BaseEntity


class WebSharingManager(BaseEntity):

    @property
    def entity_type_name(self):
        return "SP.Sharing.WebSharingManager"
