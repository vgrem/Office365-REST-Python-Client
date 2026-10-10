from __future__ import annotations

from dataclasses import dataclass, field

from office365.communications.comms_notification import CommsNotification
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class CommsNotifications(ClientValue):
    value: ClientValueCollection[CommsNotification] = field(
        default_factory=lambda: ClientValueCollection(CommsNotification)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CommsNotifications"
