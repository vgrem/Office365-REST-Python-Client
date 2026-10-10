from __future__ import annotations

from dataclasses import dataclass, field

from office365.common.sharepoint_embedded_configuration import (
    SharePointEmbeddedConfiguration,
)
from office365.runtime.client_value import ClientValue
from office365.search.external.item_configuration import ExternalItemConfiguration


@dataclass
class DataSourceConfiguration(ClientValue):
    externalItem: ExternalItemConfiguration = field(default_factory=ExternalItemConfiguration)
    sharePointEmbedded: SharePointEmbeddedConfiguration = field(default_factory=SharePointEmbeddedConfiguration)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DataSourceConfiguration"
