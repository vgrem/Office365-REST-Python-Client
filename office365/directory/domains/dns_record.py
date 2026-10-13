from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class DomainDnsRecord(Entity):
    """
    For each domain in the tenant, you may be required to add DNS record(s) to the DNS zone file of the domain before
    the domain can be used by Microsoft Online Services. These DNS records are represented
    """

    @property
    def is_optional(self) -> Optional[bool]:
        """Gets the isOptional property"""
        return self.properties.get("isOptional", None)

    @property
    def label(self) -> Optional[str]:
        """Gets the label property"""
        return self.properties.get("label", None)

    @property
    def record_type(self) -> Optional[str]:
        """Gets the recordType property"""
        return self.properties.get("recordType", None)

    @property
    def supported_service(self) -> Optional[str]:
        """Gets the supportedService property"""
        return self.properties.get("supportedService", None)

    @property
    def ttl(self) -> Optional[int]:
        """Gets the ttl property"""
        return self.properties.get("ttl", None)

    @property
    def value(self) -> Optional[str]:
        """Target value to publish in the DNS zone file.

        Depending on :attr:`record_type` the server stores it under a different
        name (``canonicalName`` for CNAME, ``text`` for TXT, ``mailExchange``
        for MX, ``nameTarget`` for SRV); this convenience property surfaces the
        first one that is present so callers do not have to branch.
        """
        for name in ("canonicalName", "text", "mailExchange", "nameTarget"):
            if name in self.properties:
                return self.properties[name]
        return None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DomainDnsRecord"
