from typing import Optional

from office365.sharepoint.entity import Entity
from office365.sharepoint.sharing.principal import Principal


class SharedDocumentInfo(Entity):
    """"""

    @property
    def activity(self):
        # type: () -> Optional[str]
        """"""
        return self.properties.get("Activity", None)

    @property
    def author(self):
        """"""
        return self.properties.get("Author", Principal())

    @property
    def caller_stack(self):
        # type: () -> Optional[str]
        """"""
        return self.properties.get("CallerStack", None)

    @property
    def entity_type_name(self):
        return "SP.Sharing.SharedDocumentInfo"
