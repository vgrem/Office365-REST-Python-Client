from __future__ import annotations

from dataclasses import dataclass, field

from office365.externalconnectors.url_to_item_resolver_base import UrlToItemResolverBase
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class ActivitySettings(ClientValue):
    urlToItemResolvers: ClientValueCollection[UrlToItemResolverBase] = field(
        default_factory=lambda: ClientValueCollection(UrlToItemResolverBase)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.externalConnectors.ActivitySettings"
