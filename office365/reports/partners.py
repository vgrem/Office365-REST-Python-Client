from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.partners.billing.billing import Billing


class Partners(Entity):
    @property
    def billing(self) -> Billing:
        """Gets the billing property"""
        from office365.partners.billing.billing import Billing

        return self.properties.get("billing", Billing(self.context, ResourcePath("billing", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Partners"
