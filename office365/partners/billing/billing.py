from __future__ import annotations

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.partners.billing.azure_usage import AzureUsage
from office365.partners.billing.manifest import Manifest
from office365.partners.billing.operation import Operation
from office365.partners.billing.reconciliation import BillingReconciliation
from office365.runtime.paths.resource_path import ResourcePath


class Billing(Entity):
    @property
    def manifests(self) -> EntityCollection[Manifest]:
        """Gets the manifests property"""
        return self.properties.get(
            "manifests",
            EntityCollection[Manifest](self.context, Manifest, ResourcePath("manifests", self.resource_path)),
        )

    @property
    def operations(self) -> EntityCollection[Operation]:
        """Gets the operations property"""
        return self.properties.get(
            "operations",
            EntityCollection[Operation](self.context, Operation, ResourcePath("operations", self.resource_path)),
        )

    @property
    def reconciliation(self) -> BillingReconciliation:
        """Gets the reconciliation property"""
        return self.properties.get(
            "reconciliation", BillingReconciliation(self.context, ResourcePath("reconciliation", self.resource_path))
        )

    @property
    def usage(self) -> AzureUsage:
        """Gets the usage property"""
        return self.properties.get("usage", AzureUsage(self.context, ResourcePath("usage", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.partners.billing.Billing"
