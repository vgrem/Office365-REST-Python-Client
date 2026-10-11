from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.audit.audit_record_type_dictionary import AuditRecordTypeDictionary


@dataclass
class AuditData(ClientValue):
    dynamicProperties: AuditRecordTypeDictionary = field(default_factory=AuditRecordTypeDictionary)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AuditData"
