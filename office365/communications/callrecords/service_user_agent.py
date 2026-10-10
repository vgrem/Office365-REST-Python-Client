from __future__ import annotations

from dataclasses import dataclass

from office365.communications.callrecords.service_role import ServiceRole
from office365.runtime.client_value import ClientValue


@dataclass
class ServiceUserAgent(ClientValue):
    role: ServiceRole = ServiceRole.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.ServiceUserAgent"
