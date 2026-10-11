from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.authentication.strength.root import AuthenticationStrengthRoot
from office365.directory.identities.named_location import NamedLocation
from office365.directory.policies.authentication_context_class_reference import (
    AuthenticationContextClassReference,
)
from office365.directory.policies.ca_policies_deletable_root import (
    CaPoliciesDeletableRoot,
)
from office365.directory.policies.conditionalaccess.conditional_access import (
    ConditionalAccessPolicy,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identities.conditional_access_template import (
        ConditionalAccessTemplate,
    )


class ConditionalAccessRoot(Entity):
    """The conditionalAccessRoot resource is the entry point for the Conditional Access (CA) object model.
    It doesn't contain any usable properties."""

    @property
    def authentication_strength(self) -> AuthenticationStrengthRoot:
        """The entry point for the Conditional Access (CA) object model."""
        return self.properties.get(
            "authenticationStrength",
            AuthenticationStrengthRoot(self.context, ResourcePath("authenticationStrength", self.resource_path)),
        )

    @property
    def policies(self) -> EntityCollection[ConditionalAccessPolicy]:
        """Returns a collection of the specified Conditional Access (CA) policies."""
        return self.properties.get(
            "policies",
            EntityCollection(self.context, ConditionalAccessPolicy, ResourcePath("policies", self.resource_path)),
        )

    @property
    def authentication_context_class_references(self) -> EntityCollection[AuthenticationContextClassReference]:
        """Gets the authenticationContextClassReferences property"""
        return self.properties.get(
            "authenticationContextClassReferences",
            EntityCollection[AuthenticationContextClassReference](
                self.context,
                AuthenticationContextClassReference,
                ResourcePath("authenticationContextClassReferences", self.resource_path),
            ),
        )

    @property
    def deleted_items(self) -> CaPoliciesDeletableRoot:
        """Gets the deletedItems property"""
        return self.properties.get(
            "deletedItems", CaPoliciesDeletableRoot(self.context, ResourcePath("deletedItems", self.resource_path))
        )

    @property
    def named_locations(self) -> EntityCollection[NamedLocation]:
        """Gets the namedLocations property"""
        return self.properties.get(
            "namedLocations",
            EntityCollection[NamedLocation](
                self.context, NamedLocation, ResourcePath("namedLocations", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ConditionalAccessRoot"

    @property
    def templates(self) -> EntityCollection[ConditionalAccessTemplate]:
        """Gets the templates property"""
        from office365.directory.identities.conditional_access_template import (
            ConditionalAccessTemplate,
        )

        return self.properties.get(
            "templates",
            EntityCollection[ConditionalAccessTemplate](
                self.context, ConditionalAccessTemplate, ResourcePath("templates", self.resource_path)
            ),
        )
