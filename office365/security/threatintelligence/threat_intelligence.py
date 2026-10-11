from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.article import Article
from office365.security.audit.whois_history_record import WhoisHistoryRecord
from office365.security.audit.whois_record import WhoisRecord
from office365.security.intelligence_profile_indicator import IntelligenceProfileIndicator
from office365.security.passive_dns_record import PassiveDnsRecord
from office365.security.ssl_certificate import SslCertificate
from office365.security.subdomain import Subdomain
from office365.security.threatintelligence.article_indicator import ArticleIndicator
from office365.security.threatintelligence.host import Host
from office365.security.threatintelligence.host_component import HostComponent
from office365.security.threatintelligence.host_cookie import HostCookie
from office365.security.threatintelligence.host_pair import HostPair
from office365.security.threatintelligence.host_port import HostPort
from office365.security.threatintelligence.host_ssl_certificate import HostSslCertificate
from office365.security.threatintelligence.host_tracker import HostTracker
from office365.security.threatintelligence.profile import IntelligenceProfile
from office365.security.vulnerability import Vulnerability


class ThreatIntelligence(Entity):
    """
    Provides APIs to retrieve threat intelligence information, such as about a host or an article on a threat.

    The Microsoft Graph threat intelligence API delivers world-class threat intelligence to help protect your
    organization from modern cyber threats. Using threat intelligence APIs, you can identify adversaries and their
    operations, accelerate detection and remediation, and enhance your security investments and workflows.

    The threat intelligence API allows you to operationalize intelligence found within the user interface.
    This includes finished intelligence in the forms of articles and intel profiles, machine intelligence including
    indicators of compromise (IoCs) and reputation verdicts, and finally, enrichment data including passive DNS,
    cookies, components, and trackers.
    """

    @property
    def article_indicators(self) -> EntityCollection[ArticleIndicator]:
        """Gets the articleIndicators property"""
        return self.properties.get(
            "articleIndicators",
            EntityCollection[ArticleIndicator](
                self.context, ArticleIndicator, ResourcePath("articleIndicators", self.resource_path)
            ),
        )

    @property
    def articles(self) -> EntityCollection[Article]:
        """Gets the articles property"""
        return self.properties.get(
            "articles", EntityCollection[Article](self.context, Article, ResourcePath("articles", self.resource_path))
        )

    @property
    def host_components(self) -> EntityCollection[HostComponent]:
        """Gets the hostComponents property"""
        return self.properties.get(
            "hostComponents",
            EntityCollection[HostComponent](
                self.context, HostComponent, ResourcePath("hostComponents", self.resource_path)
            ),
        )

    @property
    def host_cookies(self) -> EntityCollection[HostCookie]:
        """Gets the hostCookies property"""
        return self.properties.get(
            "hostCookies",
            EntityCollection[HostCookie](self.context, HostCookie, ResourcePath("hostCookies", self.resource_path)),
        )

    @property
    def host_pairs(self) -> EntityCollection[HostPair]:
        """Gets the hostPairs property"""
        return self.properties.get(
            "hostPairs",
            EntityCollection[HostPair](self.context, HostPair, ResourcePath("hostPairs", self.resource_path)),
        )

    @property
    def host_ports(self) -> EntityCollection[HostPort]:
        """Gets the hostPorts property"""
        return self.properties.get(
            "hostPorts",
            EntityCollection[HostPort](self.context, HostPort, ResourcePath("hostPorts", self.resource_path)),
        )

    @property
    def hosts(self) -> EntityCollection[Host]:
        """Gets the hosts property"""
        return self.properties.get(
            "hosts", EntityCollection[Host](self.context, Host, ResourcePath("hosts", self.resource_path))
        )

    @property
    def host_ssl_certificates(self) -> EntityCollection[HostSslCertificate]:
        """Gets the hostSslCertificates property"""
        return self.properties.get(
            "hostSslCertificates",
            EntityCollection[HostSslCertificate](
                self.context, HostSslCertificate, ResourcePath("hostSslCertificates", self.resource_path)
            ),
        )

    @property
    def host_trackers(self) -> EntityCollection[HostTracker]:
        """Gets the hostTrackers property"""
        return self.properties.get(
            "hostTrackers",
            EntityCollection[HostTracker](self.context, HostTracker, ResourcePath("hostTrackers", self.resource_path)),
        )

    @property
    def intelligence_profile_indicators(self) -> EntityCollection[IntelligenceProfileIndicator]:
        """Gets the intelligenceProfileIndicators property"""
        return self.properties.get(
            "intelligenceProfileIndicators",
            EntityCollection[IntelligenceProfileIndicator](
                self.context,
                IntelligenceProfileIndicator,
                ResourcePath("intelligenceProfileIndicators", self.resource_path),
            ),
        )

    @property
    def intel_profiles(self) -> EntityCollection[IntelligenceProfile]:
        """Gets the intelProfiles property"""
        return self.properties.get(
            "intelProfiles",
            EntityCollection[IntelligenceProfile](
                self.context, IntelligenceProfile, ResourcePath("intelProfiles", self.resource_path)
            ),
        )

    @property
    def passive_dns_records(self) -> EntityCollection[PassiveDnsRecord]:
        """Gets the passiveDnsRecords property"""
        return self.properties.get(
            "passiveDnsRecords",
            EntityCollection[PassiveDnsRecord](
                self.context, PassiveDnsRecord, ResourcePath("passiveDnsRecords", self.resource_path)
            ),
        )

    @property
    def ssl_certificates(self) -> EntityCollection[SslCertificate]:
        """Gets the sslCertificates property"""
        return self.properties.get(
            "sslCertificates",
            EntityCollection[SslCertificate](
                self.context, SslCertificate, ResourcePath("sslCertificates", self.resource_path)
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
    def vulnerabilities(self) -> EntityCollection[Vulnerability]:
        """Gets the vulnerabilities property"""
        return self.properties.get(
            "vulnerabilities",
            EntityCollection[Vulnerability](
                self.context, Vulnerability, ResourcePath("vulnerabilities", self.resource_path)
            ),
        )

    @property
    def whois_history_records(self) -> EntityCollection[WhoisHistoryRecord]:
        """Gets the whoisHistoryRecords property"""
        return self.properties.get(
            "whoisHistoryRecords",
            EntityCollection[WhoisHistoryRecord](
                self.context, WhoisHistoryRecord, ResourcePath("whoisHistoryRecords", self.resource_path)
            ),
        )

    @property
    def whois_records(self) -> EntityCollection[WhoisRecord]:
        """Gets the whoisRecords property"""
        return self.properties.get(
            "whoisRecords",
            EntityCollection[WhoisRecord](self.context, WhoisRecord, ResourcePath("whoisRecords", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.ThreatIntelligence"
