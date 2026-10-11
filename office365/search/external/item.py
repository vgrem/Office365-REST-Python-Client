from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.externalconnectors.external_activity import ExternalActivity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.externalconnectors.acl import Acl
    from office365.externalconnectors.external_item_content import ExternalItemContent
    from office365.externalconnectors.external_item_information_protection_label import (
        ExternalItemInformationProtectionLabel,
    )


class ExternalItem(Entity):
    """An item added to a Microsoft Graph connection."""

    @property
    def activities(self) -> EntityCollection[ExternalActivity]:
        """Gets the activities property"""
        return self.properties.get(
            "activities",
            EntityCollection[ExternalActivity](
                self.context, ExternalActivity, ResourcePath("activities", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.externalConnectors.ExternalItem"

    @property
    def acl(self) -> ClientValueCollection[Acl]:
        """Gets the acl property"""
        from office365.externalconnectors.acl import Acl

        return self.properties.get("acl", ClientValueCollection[Acl](Acl))

    @property
    def content(self) -> Optional[ExternalItemContent]:
        """Gets the content property"""
        return self.properties.get("content", None)

    @property
    def information_protection_label(self) -> Optional[ExternalItemInformationProtectionLabel]:
        """Gets the informationProtectionLabel property"""
        return self.properties.get("informationProtectionLabel", None)
