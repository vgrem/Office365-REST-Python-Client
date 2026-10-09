from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, cast

from office365.runtime.client_value import ClientValue
from office365.runtime.converters.scalars import iso_z
from office365.runtime.types.collections import StringCollection


@dataclass
class SubscriptionInformation(ClientValue):
    """Parameter class for webhook Update and Create REST operations."""

    notificationUrl: Optional[str] = None
    resource: Optional[str] = None
    expirationDateTime: datetime = field(default_factory=lambda: datetime.min)
    clientState: Optional[str] = None
    resourceData: Optional[str] = None
    scenarios: StringCollection = field(default_factory=StringCollection)

    def to_json(self, json_format=None):
        json = cast(Dict, super().to_json(json_format))
        json["expirationDateTime"] = iso_z(self.expirationDateTime)
        return json

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Webhooks.SubscriptionInformation"
