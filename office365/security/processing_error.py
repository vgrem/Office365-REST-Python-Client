from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue
from office365.security.contentprocessingerrortype import ContentProcessingErrorType


@dataclass
class ProcessingError(ClientValue):
    errorType: ContentProcessingErrorType = ContentProcessingErrorType.transient

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProcessingError"
