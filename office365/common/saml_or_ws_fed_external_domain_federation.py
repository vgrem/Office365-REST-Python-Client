from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.external_domain_name import ExternalDomainName


class SamlOrWsFedExternalDomainFederation(Entity):
    @property
    def domains(self) -> EntityCollection[ExternalDomainName]:
        """Gets the domains property"""
        from office365.common.external_domain_name import ExternalDomainName

        return self.properties.get(
            "domains",
            EntityCollection[ExternalDomainName](
                self.context, ExternalDomainName, ResourcePath("domains", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SamlOrWsFedExternalDomainFederation"
