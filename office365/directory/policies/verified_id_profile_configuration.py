from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.claim_binding import ClaimBinding
from office365.directory.claim_binding_source import ClaimBindingSource
from office365.directory.claim_validation import ClaimValidation
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class VerifiedIdProfileConfiguration(ClientValue):
    acceptedIssuer: str | None = None
    type: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VerifiedIdProfileConfiguration"

    claimBindings: ClientValueCollection[ClaimBinding] = field(
        default_factory=lambda: ClientValueCollection(ClaimBinding)
    )

    claimValidation: ClaimValidation = field(default_factory=ClaimValidation)

    claimBindingSource: ClaimBindingSource = ClaimBindingSource.directory
