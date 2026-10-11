from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.partners.billing.billed_reconciliation import BilledReconciliation
    from office365.partners.billing.unbilled_reconciliation import (
        UnbilledReconciliation,
    )


class BillingReconciliation(Entity):
    @property
    def billed(self) -> BilledReconciliation:
        """Gets the billed property"""
        from office365.partners.billing.billed_reconciliation import (
            BilledReconciliation,
        )

        return self.properties.get(
            "billed", BilledReconciliation(self.context, ResourcePath("billed", self.resource_path))
        )

    @property
    def unbilled(self) -> UnbilledReconciliation:
        """Gets the unbilled property"""
        from office365.partners.billing.unbilled_reconciliation import (
            UnbilledReconciliation,
        )

        return self.properties.get(
            "unbilled", UnbilledReconciliation(self.context, ResourcePath("unbilled", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.partners.billing.BillingReconciliation"
