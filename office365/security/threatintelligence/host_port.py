from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.security.ssl_certificate import SslCertificate

if TYPE_CHECKING:
    from office365.security.threatintelligence.host import Host
    from office365.security.threatintelligence.host_port_banner import (
        HostPortBanner,
    )
    from office365.security.threatintelligence.host_port_component import (
        HostPortComponent,
    )
    from office365.security.threatintelligence.host_port_protocol import (
        HostPortProtocol,
    )
    from office365.security.threatintelligence.host_port_status import (
        HostPortStatus,
    )


class HostPort(Entity):
    @property
    def first_seen_date_time(self) -> datetime:
        """Gets the firstSeenDateTime property"""
        return self.properties.get("firstSeenDateTime", datetime.min)

    @property
    def last_scan_date_time(self) -> datetime:
        """Gets the lastScanDateTime property"""
        return self.properties.get("lastScanDateTime", datetime.min)

    @property
    def last_seen_date_time(self) -> datetime:
        """Gets the lastSeenDateTime property"""
        return self.properties.get("lastSeenDateTime", datetime.min)

    @property
    def port(self) -> Optional[int]:
        """Gets the port property"""
        return self.properties.get("port", None)

    @property
    def times_observed(self) -> Optional[int]:
        """Gets the timesObserved property"""
        return self.properties.get("timesObserved", None)

    @property
    def host(self) -> Host:
        """Gets the host property"""
        return self.properties.get("host", Host(self.context, ResourcePath("host", self.resource_path)))

    @odata(name="mostRecentSslCertificate")
    @property
    def most_recent_ssl_certificate(self) -> SslCertificate:
        """Gets the mostRecentSslCertificate property"""
        return self.properties.get(
            "mostRecentSslCertificate",
            SslCertificate(self.context, ResourcePath("mostRecentSslCertificate", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.HostPort"

    @property
    def banners(self) -> ClientValueCollection[HostPortBanner]:
        """Gets the banners property"""
        from office365.security.threatintelligence.host_port_banner import (
            HostPortBanner,
        )

        return self.properties.get("banners", ClientValueCollection[HostPortBanner](HostPortBanner))

    @property
    def protocol(self) -> HostPortProtocol:
        """Gets the protocol property"""
        from office365.security.threatintelligence.host_port_protocol import (
            HostPortProtocol,
        )

        return self.properties.get("protocol", HostPortProtocol.tcp)

    @property
    def services(self) -> ClientValueCollection[HostPortComponent]:
        """Gets the services property"""
        from office365.security.threatintelligence.host_port_component import (
            HostPortComponent,
        )

        return self.properties.get("services", ClientValueCollection[HostPortComponent](HostPortComponent))

    @property
    def status(self) -> HostPortStatus:
        """Gets the status property"""
        from office365.security.threatintelligence.host_port_status import (
            HostPortStatus,
        )

        return self.properties.get("status", HostPortStatus.open)
