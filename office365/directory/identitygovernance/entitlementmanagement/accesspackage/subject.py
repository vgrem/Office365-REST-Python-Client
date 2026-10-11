from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.directory.identitygovernance.entitlementmanagement.accesspackage.subjecttype import (
    AccessPackageSubjectType,
)
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.subject_lifecycle import (
        AccessPackageSubjectLifecycle,
    )
    from office365.directory.identitygovernance.entitlementmanagement.connected_organization import (
        ConnectedOrganization,
    )


class AccessPackageSubject(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def email(self) -> Optional[str]:
        """Gets the email property"""
        return self.properties.get("email", None)

    @property
    def object_id(self) -> Optional[str]:
        """Gets the objectId property"""
        return self.properties.get("objectId", None)

    @property
    def on_premises_security_identifier(self) -> Optional[str]:
        """Gets the onPremisesSecurityIdentifier property"""
        return self.properties.get("onPremisesSecurityIdentifier", None)

    @property
    def principal_name(self) -> Optional[str]:
        """Gets the principalName property"""
        return self.properties.get("principalName", None)

    @property
    def subject_type(self) -> AccessPackageSubjectType:
        """Gets the subjectType property"""
        return self.properties.get("subjectType", AccessPackageSubjectType.notSpecified)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessPackageSubject"

    @property
    def subject_lifecycle(self) -> AccessPackageSubjectLifecycle:
        """Gets the subjectLifecycle property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.subject_lifecycle import (
            AccessPackageSubjectLifecycle,
        )

        return self.properties.get("subjectLifecycle", AccessPackageSubjectLifecycle.notDefined)

    @property
    def connected_organization(self) -> ConnectedOrganization:
        """Gets the connectedOrganization property"""
        from office365.directory.identitygovernance.entitlementmanagement.connected_organization import (
            ConnectedOrganization,
        )

        return self.properties.get(
            "connectedOrganization",
            ConnectedOrganization(self.context, ResourcePath("connectedOrganization", self.resource_path)),
        )
