from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.b2b_registration_metrics_initial import (
        B2BRegistrationMetricsInitial,
    )
    from office365.directory.b2b_registration_metrics_recent import (
        B2BRegistrationMetricsRecent,
    )


class B2bRegistrationMetrics(Entity):
    @property
    def initial(self) -> B2BRegistrationMetricsInitial:
        """Gets the initial property"""
        from office365.directory.b2b_registration_metrics_initial import (
            B2BRegistrationMetricsInitial,
        )

        return self.properties.get(
            "initial", B2BRegistrationMetricsInitial(self.context, ResourcePath("initial", self.resource_path))
        )

    @property
    def recent(self) -> B2BRegistrationMetricsRecent:
        """Gets the recent property"""
        from office365.directory.b2b_registration_metrics_recent import (
            B2BRegistrationMetricsRecent,
        )

        return self.properties.get(
            "recent", B2BRegistrationMetricsRecent(self.context, ResourcePath("recent", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.B2bRegistrationMetrics"
