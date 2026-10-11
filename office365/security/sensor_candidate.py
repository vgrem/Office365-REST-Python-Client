from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class SensorCandidate(Entity):
    @property
    def computer_dns_name(self) -> Optional[str]:
        """Gets the computerDnsName property"""
        return self.properties.get("computerDnsName", None)

    @property
    def domain_name(self) -> Optional[str]:
        """Gets the domainName property"""
        return self.properties.get("domainName", None)

    @property
    def last_seen_date_time(self) -> datetime:
        """Gets the lastSeenDateTime property"""
        return self.properties.get("lastSeenDateTime", datetime.min)

    @property
    def sense_client_version(self) -> Optional[str]:
        """Gets the senseClientVersion property"""
        return self.properties.get("senseClientVersion", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.SensorCandidate"
