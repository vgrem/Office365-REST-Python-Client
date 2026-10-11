from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.datasecurity.dlp_action_info import DlpActionInfo
from office365.security.processing_error import ProcessingError
from office365.security.protectionscopestate import ProtectionScopeState


@dataclass
class ProcessContentResponse(ClientValue):
    policyActions: ClientValueCollection[DlpActionInfo] = field(
        default_factory=lambda: ClientValueCollection(DlpActionInfo)
    )
    processingErrors: ClientValueCollection[ProcessingError] = field(
        default_factory=lambda: ClientValueCollection(ProcessingError)
    )
    protectionScopeState: ProtectionScopeState = ProtectionScopeState.notModified

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProcessContentResponse"
