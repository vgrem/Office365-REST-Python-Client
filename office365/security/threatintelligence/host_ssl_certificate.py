from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.security.ssl_certificate import SslCertificate

if TYPE_CHECKING:
    from office365.security.host_ssl_certificate_port import (
        HostSslCertificatePort,
    )
    from office365.security.threatintelligence.host import Host


class HostSslCertificate(Entity):
    @odata(name="firstSeenDateTime")
    @property
    def first_seen_date_time(self) -> datetime:
        """Gets the firstSeenDateTime property"""
        return self.properties.get("firstSeenDateTime", datetime.min)

    @odata(name="lastSeenDateTime")
    @property
    def last_seen_date_time(self) -> datetime:
        """Gets the lastSeenDateTime property"""
        return self.properties.get("lastSeenDateTime", datetime.min)

    @property
    def host(self) -> Host:
        """Gets the host property"""
        return self.properties.get("host", Host(self.context, ResourcePath("host", self.resource_path)))

    @odata(name="sslCertificate")
    @property
    def ssl_certificate(self) -> SslCertificate:
        """Gets the sslCertificate property"""
        return self.properties.get(
            "sslCertificate", SslCertificate(self.context, ResourcePath("sslCertificate", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.HostSslCertificate"

    @property
    def ports(self) -> ClientValueCollection[HostSslCertificatePort]:
        """Gets the ports property"""
        from office365.security.host_ssl_certificate_port import (
            HostSslCertificatePort,
        )

        return self.properties.get("ports", ClientValueCollection[HostSslCertificatePort](HostSslCertificatePort))
