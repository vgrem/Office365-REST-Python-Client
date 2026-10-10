from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue
from office365.subscriptions.changetype import ChangeType


@dataclass
class CommsNotification(ClientValue):
    changeType: ChangeType = ChangeType.created

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CommsNotification"
