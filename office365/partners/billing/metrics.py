from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.partners.billing.metrics_initial import BillingMetricsInitial
    from office365.partners.billing.metrics_recent import BillingMetricsRecent


class BillingMetrics(Entity):
    @property
    def initial(self) -> BillingMetricsInitial:
        """Gets the initial property"""
        from office365.partners.billing.metrics_initial import BillingMetricsInitial

        return self.properties.get(
            "initial", BillingMetricsInitial(self.context, ResourcePath("initial", self.resource_path))
        )

    @property
    def recent(self) -> BillingMetricsRecent:
        """Gets the recent property"""
        from office365.partners.billing.metrics_recent import BillingMetricsRecent

        return self.properties.get(
            "recent", BillingMetricsRecent(self.context, ResourcePath("recent", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BillingMetrics"
