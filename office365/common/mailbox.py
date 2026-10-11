from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.mailbox_folder import MailboxFolder


class Mailbox(Entity):
    @property
    def folders(self) -> EntityCollection[MailboxFolder]:
        """Gets the folders property"""
        from office365.common.mailbox_folder import MailboxFolder

        return self.properties.get(
            "folders",
            EntityCollection[MailboxFolder](self.context, MailboxFolder, ResourcePath("folders", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Mailbox"
