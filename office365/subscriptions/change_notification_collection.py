from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection
from office365.subscriptions.change_notification import ChangeNotification


@dataclass
class ChangeNotificationCollection(ClientValue):
    """Represents a collection of resource change notifications sent to the subscriber."""

    validationTokens: StringCollection = field(default_factory=StringCollection)
    value: ClientValueCollection = field(default_factory=lambda: ClientValueCollection(ChangeNotification))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ChangeNotificationCollection"
