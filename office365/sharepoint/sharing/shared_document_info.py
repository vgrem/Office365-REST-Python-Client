from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sharing.principal import Principal


class SharedDocumentInfo(BaseEntity):
    """"""

    @property
    def activity(self):
        """"""
        return self.properties.get("Activity", None)

    @property
    def author(self):
        """"""
        return self.properties.get("Author", Principal())

    @property
    def entity_type_name(self):
        return "SP.Sharing.SharedDocumentInfo"
