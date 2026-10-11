from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.protection.bitlocker_recovery_key import (
        BitlockerRecoveryKey,
    )


class Bitlocker(Entity):
    @property
    def recovery_keys(self) -> EntityCollection[BitlockerRecoveryKey]:
        """Gets the recoveryKeys property"""
        from office365.directory.protection.bitlocker_recovery_key import (
            BitlockerRecoveryKey,
        )

        return self.properties.get(
            "recoveryKeys",
            EntityCollection[BitlockerRecoveryKey](
                self.context, BitlockerRecoveryKey, ResourcePath("recoveryKeys", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Bitlocker"
