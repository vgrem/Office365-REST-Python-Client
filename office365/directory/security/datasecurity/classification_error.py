from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.datasecurity.classifcation_error_base import (
    ClassifcationErrorBase,
)
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class ClassificationError(ClientValue):
    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ClassificationError"

    details: ClientValueCollection[ClassifcationErrorBase] = field(
        default_factory=lambda: ClientValueCollection(ClassifcationErrorBase)
    )
