from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class DomainDnsSrvRecord(Entity):
    @property
    def name_target(self) -> Optional[str]:
        """Gets the nameTarget property"""
        return self.properties.get("nameTarget", None)

    @property
    def port(self) -> Optional[int]:
        """Gets the port property"""
        return self.properties.get("port", None)

    @property
    def priority(self) -> Optional[int]:
        """Gets the priority property"""
        return self.properties.get("priority", None)

    @property
    def protocol(self) -> Optional[str]:
        """Gets the protocol property"""
        return self.properties.get("protocol", None)

    @property
    def service(self) -> Optional[str]:
        """Gets the service property"""
        return self.properties.get("service", None)

    @property
    def weight(self) -> Optional[int]:
        """Gets the weight property"""
        return self.properties.get("weight", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DomainDnsSrvRecord"
