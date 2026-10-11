from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.b2b_sign_in_activity_metrics_initial import (
        B2BSignInActivityMetricsInitial,
    )
    from office365.directory.b2b_sign_in_activity_metrics_recent import (
        B2BSignInActivityMetricsRecent,
    )


class B2BSignInActivityMetrics(Entity):
    @property
    def initial(self) -> B2BSignInActivityMetricsInitial:
        """Gets the initial property"""
        from office365.directory.b2b_sign_in_activity_metrics_initial import (
            B2BSignInActivityMetricsInitial,
        )

        return self.properties.get(
            "initial", B2BSignInActivityMetricsInitial(self.context, ResourcePath("initial", self.resource_path))
        )

    @property
    def recent(self) -> B2BSignInActivityMetricsRecent:
        """Gets the recent property"""
        from office365.directory.b2b_sign_in_activity_metrics_recent import (
            B2BSignInActivityMetricsRecent,
        )

        return self.properties.get(
            "recent", B2BSignInActivityMetricsRecent(self.context, ResourcePath("recent", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.B2BSignInActivityMetrics"
