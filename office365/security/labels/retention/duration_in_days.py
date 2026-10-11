from __future__ import annotations

from dataclasses import dataclass

from office365.security.labels.retention.duration import RetentionDuration


@dataclass
class RetentionDurationInDays(RetentionDuration):
    """"""

    days: int | None = None

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.retentionDurationInDays"
