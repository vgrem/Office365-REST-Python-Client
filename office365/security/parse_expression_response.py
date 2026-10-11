from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.public_error import PublicError
from office365.security.attribute_mapping_source import AttributeMappingSource


@dataclass
class ParseExpressionResponse(ClientValue):
    evaluationResult: StringCollection = field(default_factory=StringCollection)
    evaluationSucceeded: bool | None = None
    parsedExpression: AttributeMappingSource = field(default_factory=AttributeMappingSource)
    parsingSucceeded: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ParseExpressionResponse"

    error: PublicError = field(default_factory=PublicError)
