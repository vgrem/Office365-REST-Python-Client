from __future__ import annotations

from dataclasses import dataclass, field

from office365.common.key_value import KeyValue
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class ContentCustomization(ClientValue):
    attributeCollectionRelativeUrl: str | None = None
    registrationCampaignRelativeUrl: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ContentCustomization"

    attributeCollection: ClientValueCollection[KeyValue] = field(default_factory=lambda: ClientValueCollection(KeyValue))

    registrationCampaign: ClientValueCollection[KeyValue] = field(
        default_factory=lambda: ClientValueCollection(KeyValue)
    )
