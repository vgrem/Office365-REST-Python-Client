from __future__ import annotations

from dataclasses import dataclass

from office365.communications.callrecords.clientplatform import ClientPlatform
from office365.communications.callrecords.product_family import ProductFamily
from office365.runtime.client_value import ClientValue


@dataclass
class ClientUserAgent(ClientValue):
    azureADAppId: str | None = None
    communicationServiceId: str | None = None
    platform: ClientPlatform = ClientPlatform.unknown
    productFamily: ProductFamily = ProductFamily.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.ClientUserAgent"
