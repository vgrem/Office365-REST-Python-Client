from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.security.alerts.feedback import AlertFeedback
from office365.security.alerts.status import AlertStatus


@dataclass
class AlertHistoryState(ClientValue):
    """
    Stores changes made to alerts.
    """

    appId: str | None = None
    assignedTo: str | None = None
    comments: list[str] | None = None

    feedback: AlertFeedback = AlertFeedback.unknown

    status: AlertStatus = AlertStatus.unknown

    updatedDateTime: datetime | None = None

    user: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AlertHistoryState"
