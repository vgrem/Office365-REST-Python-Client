from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.verified_id_profile import VerifiedIdProfile


class IdentityVerifiedIdRoot(Entity):
    @property
    def profiles(self) -> EntityCollection[VerifiedIdProfile]:
        """Gets the profiles property"""
        from office365.directory.verified_id_profile import VerifiedIdProfile

        return self.properties.get(
            "profiles",
            EntityCollection[VerifiedIdProfile](
                self.context, VerifiedIdProfile, ResourcePath("profiles", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IdentityVerifiedIdRoot"
