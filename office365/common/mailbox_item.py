from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.extensions.extended_property import (
        MultiValueLegacyExtendedProperty,
        SingleValueLegacyExtendedProperty,
    )


class MailboxItem(Entity):
    @property
    def size(self) -> Optional[int]:
        """Gets the size property"""
        return self.properties.get("size", None)

    @property
    def type(self) -> Optional[str]:
        """Gets the type property"""
        return self.properties.get("type", None)

    @property
    def multi_value_extended_properties(self) -> EntityCollection[MultiValueLegacyExtendedProperty]:
        """Gets the multiValueExtendedProperties property"""
        from office365.directory.extensions.extended_property import (
            MultiValueLegacyExtendedProperty,
        )

        return self.properties.get(
            "multiValueExtendedProperties",
            EntityCollection[MultiValueLegacyExtendedProperty](
                self.context,
                MultiValueLegacyExtendedProperty,
                ResourcePath("multiValueExtendedProperties", self.resource_path),
            ),
        )

    @property
    def single_value_extended_properties(self) -> EntityCollection[SingleValueLegacyExtendedProperty]:
        """Gets the singleValueExtendedProperties property"""
        from office365.directory.extensions.extended_property import (
            SingleValueLegacyExtendedProperty,
        )

        return self.properties.get(
            "singleValueExtendedProperties",
            EntityCollection[SingleValueLegacyExtendedProperty](
                self.context,
                SingleValueLegacyExtendedProperty,
                ResourcePath("singleValueExtendedProperties", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MailboxItem"
