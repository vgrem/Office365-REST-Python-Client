from __future__ import annotations

from enum import Enum


class WhoisDomainStatus(Enum):
    clientDeleteProhibited = "0"
    clientHold = "1"
    clientRenewProhibited = "2"
    clientTransferProhibited = "3"
    clientUpdateProhibited = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.WhoisDomainStatus"
