from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.key_value_pair import KeyValuePair


@dataclass
class SubjectRightsRequestDetail(ClientValue):
    excludedItemCount: int | None = None
    insightCounts: ClientValueCollection[KeyValuePair] = field(
        default_factory=lambda: ClientValueCollection(KeyValuePair)
    )
    itemCount: int | None = None
    itemNeedReview: int | None = None
    productItemCounts: ClientValueCollection[KeyValuePair] = field(
        default_factory=lambda: ClientValueCollection(KeyValuePair)
    )
    signedOffItemCount: int | None = None
    totalItemSize: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SubjectRightsRequestDetail"
