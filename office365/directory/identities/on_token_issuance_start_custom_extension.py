from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.directory.identities.on_token_issuance_start_return_claim import (
        OnTokenIssuanceStartReturnClaim,
    )


class OnTokenIssuanceStartCustomExtension(Entity):
    @property
    def claims_for_token_configuration(self) -> ClientValueCollection[OnTokenIssuanceStartReturnClaim]:
        """Gets the claimsForTokenConfiguration property"""
        from office365.directory.identities.on_token_issuance_start_return_claim import (
            OnTokenIssuanceStartReturnClaim,
        )

        return self.properties.get(
            "claimsForTokenConfiguration",
            ClientValueCollection[OnTokenIssuanceStartReturnClaim](OnTokenIssuanceStartReturnClaim),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnTokenIssuanceStartCustomExtension"
