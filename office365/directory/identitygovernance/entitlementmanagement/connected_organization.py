from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.identitygovernance.entitlementmanagement.connectedorganizationstate import (
    ConnectedOrganizationState,
)
from office365.directory.objects.object import DirectoryObject
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.entitlementmanagement.identity_source import (
        IdentitySource,
    )


class ConnectedOrganization(Entity):
    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def modified_date_time(self) -> datetime:
        """Gets the modifiedDateTime property"""
        return self.properties.get("modifiedDateTime", datetime.min)

    @property
    def state(self) -> ConnectedOrganizationState:
        """Gets the state property"""
        return self.properties.get("state", ConnectedOrganizationState.configured)

    @property
    def external_sponsors(self) -> EntityCollection[DirectoryObject]:
        """Gets the externalSponsors property"""
        return self.properties.get(
            "externalSponsors",
            EntityCollection[DirectoryObject](
                self.context, DirectoryObject, ResourcePath("externalSponsors", self.resource_path)
            ),
        )

    @property
    def internal_sponsors(self) -> EntityCollection[DirectoryObject]:
        """Gets the internalSponsors property"""
        return self.properties.get(
            "internalSponsors",
            EntityCollection[DirectoryObject](
                self.context, DirectoryObject, ResourcePath("internalSponsors", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ConnectedOrganization"

    @property
    def identity_sources(self) -> ClientValueCollection[IdentitySource]:
        """Gets the identitySources property"""
        from office365.directory.identitygovernance.entitlementmanagement.identity_source import (
            IdentitySource,
        )

        return self.properties.get("identitySources", ClientValueCollection[IdentitySource](IdentitySource))
