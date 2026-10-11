from __future__ import annotations

from datetime import datetime

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.audit.whois_record import WhoisRecord
from office365.security.passive_dns_record import PassiveDnsRecord
from office365.security.subdomain import Subdomain
from office365.security.threatintelligence.host_component import HostComponent
from office365.security.threatintelligence.host_cookie import HostCookie
from office365.security.threatintelligence.host_pair import HostPair
from office365.security.threatintelligence.host_port import HostPort
from office365.security.threatintelligence.host_reputation import HostReputation
from office365.security.threatintelligence.host_ssl_certificate import HostSslCertificate
from office365.security.threatintelligence.host_tracker import HostTracker


class Host(Entity):
    @property
    def first_seen_date_time(self) -> datetime:
        """Gets the firstSeenDateTime property"""
        return self.properties.get("firstSeenDateTime", datetime.min)

    @property
    def last_seen_date_time(self) -> datetime:
        """Gets the lastSeenDateTime property"""
        return self.properties.get("lastSeenDateTime", datetime.min)

    @property
    def child_host_pairs(self) -> EntityCollection[HostPair]:
        """Gets the childHostPairs property"""
        return self.properties.get(
            "childHostPairs",
            EntityCollection[HostPair](self.context, HostPair, ResourcePath("childHostPairs", self.resource_path)),
        )

    @property
    def components(self) -> EntityCollection[HostComponent]:
        """Gets the components property"""
        return self.properties.get(
            "components",
            EntityCollection[HostComponent](self.context, HostComponent, ResourcePath("components", self.resource_path)),
        )

    @property
    def cookies(self) -> EntityCollection[HostCookie]:
        """Gets the cookies property"""
        return self.properties.get(
            "cookies",
            EntityCollection[HostCookie](self.context, HostCookie, ResourcePath("cookies", self.resource_path)),
        )

    @property
    def host_pairs(self) -> EntityCollection[HostPair]:
        """Gets the hostPairs property"""
        return self.properties.get(
            "hostPairs",
            EntityCollection[HostPair](self.context, HostPair, ResourcePath("hostPairs", self.resource_path)),
        )

    @property
    def parent_host_pairs(self) -> EntityCollection[HostPair]:
        """Gets the parentHostPairs property"""
        return self.properties.get(
            "parentHostPairs",
            EntityCollection[HostPair](self.context, HostPair, ResourcePath("parentHostPairs", self.resource_path)),
        )

    @property
    def passive_dns(self) -> EntityCollection[PassiveDnsRecord]:
        """Gets the passiveDns property"""
        return self.properties.get(
            "passiveDns",
            EntityCollection[PassiveDnsRecord](
                self.context, PassiveDnsRecord, ResourcePath("passiveDns", self.resource_path)
            ),
        )

    @property
    def passive_dns_reverse(self) -> EntityCollection[PassiveDnsRecord]:
        """Gets the passiveDnsReverse property"""
        return self.properties.get(
            "passiveDnsReverse",
            EntityCollection[PassiveDnsRecord](
                self.context, PassiveDnsRecord, ResourcePath("passiveDnsReverse", self.resource_path)
            ),
        )

    @property
    def ports(self) -> EntityCollection[HostPort]:
        """Gets the ports property"""
        return self.properties.get(
            "ports", EntityCollection[HostPort](self.context, HostPort, ResourcePath("ports", self.resource_path))
        )

    @property
    def reputation(self) -> HostReputation:
        """Gets the reputation property"""
        return self.properties.get(
            "reputation", HostReputation(self.context, ResourcePath("reputation", self.resource_path))
        )

    @property
    def ssl_certificates(self) -> EntityCollection[HostSslCertificate]:
        """Gets the sslCertificates property"""
        return self.properties.get(
            "sslCertificates",
            EntityCollection[HostSslCertificate](
                self.context, HostSslCertificate, ResourcePath("sslCertificates", self.resource_path)
            ),
        )

    @property
    def subdomains(self) -> EntityCollection[Subdomain]:
        """Gets the subdomains property"""
        return self.properties.get(
            "subdomains",
            EntityCollection[Subdomain](self.context, Subdomain, ResourcePath("subdomains", self.resource_path)),
        )

    @property
    def trackers(self) -> EntityCollection[HostTracker]:
        """Gets the trackers property"""
        return self.properties.get(
            "trackers",
            EntityCollection[HostTracker](self.context, HostTracker, ResourcePath("trackers", self.resource_path)),
        )

    @property
    def whois(self) -> WhoisRecord:
        """Gets the whois property"""
        return self.properties.get("whois", WhoisRecord(self.context, ResourcePath("whois", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.Host"
