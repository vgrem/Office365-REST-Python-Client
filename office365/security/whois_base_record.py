from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.threatintelligence.host import Host

if TYPE_CHECKING:
    from office365.security.whois_contact import WhoisContact
    from office365.security.whois_nameserver import WhoisNameserver


class WhoisBaseRecord(Entity):
    @property
    def domain_status(self) -> Optional[str]:
        """Gets the domainStatus property"""
        return self.properties.get("domainStatus", None)

    @property
    def expiration_date_time(self) -> datetime:
        """Gets the expirationDateTime property"""
        return self.properties.get("expirationDateTime", datetime.min)

    @property
    def first_seen_date_time(self) -> datetime:
        """Gets the firstSeenDateTime property"""
        return self.properties.get("firstSeenDateTime", datetime.min)

    @property
    def last_seen_date_time(self) -> datetime:
        """Gets the lastSeenDateTime property"""
        return self.properties.get("lastSeenDateTime", datetime.min)

    @property
    def last_update_date_time(self) -> datetime:
        """Gets the lastUpdateDateTime property"""
        return self.properties.get("lastUpdateDateTime", datetime.min)

    @property
    def raw_whois_text(self) -> Optional[str]:
        """Gets the rawWhoisText property"""
        return self.properties.get("rawWhoisText", None)

    @property
    def registration_date_time(self) -> datetime:
        """Gets the registrationDateTime property"""
        return self.properties.get("registrationDateTime", datetime.min)

    @property
    def whois_server(self) -> Optional[str]:
        """Gets the whoisServer property"""
        return self.properties.get("whoisServer", None)

    @property
    def host(self) -> Host:
        """Gets the host property"""
        return self.properties.get("host", Host(self.context, ResourcePath("host", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.WhoisBaseRecord"

    @property
    def abuse(self) -> WhoisContact:
        """Gets the abuse property"""
        from office365.security.whois_contact import WhoisContact

        return self.properties.get("abuse", WhoisContact())

    @property
    def admin(self) -> WhoisContact:
        """Gets the admin property"""
        from office365.security.whois_contact import WhoisContact

        return self.properties.get("admin", WhoisContact())

    @property
    def billing(self) -> WhoisContact:
        """Gets the billing property"""
        from office365.security.whois_contact import WhoisContact

        return self.properties.get("billing", WhoisContact())

    @property
    def nameservers(self) -> ClientValueCollection[WhoisNameserver]:
        """Gets the nameservers property"""
        from office365.security.whois_nameserver import WhoisNameserver

        return self.properties.get("nameservers", ClientValueCollection[WhoisNameserver](WhoisNameserver))

    @property
    def noc(self) -> WhoisContact:
        """Gets the noc property"""
        from office365.security.whois_contact import WhoisContact

        return self.properties.get("noc", WhoisContact())

    @property
    def registrant(self) -> WhoisContact:
        """Gets the registrant property"""
        from office365.security.whois_contact import WhoisContact

        return self.properties.get("registrant", WhoisContact())

    @property
    def registrar(self) -> WhoisContact:
        """Gets the registrar property"""
        from office365.security.whois_contact import WhoisContact

        return self.properties.get("registrar", WhoisContact())

    @property
    def technical(self) -> WhoisContact:
        """Gets the technical property"""
        from office365.security.whois_contact import WhoisContact

        return self.properties.get("technical", WhoisContact())

    @property
    def zone(self) -> WhoisContact:
        """Gets the zone property"""
        from office365.security.whois_contact import WhoisContact

        return self.properties.get("zone", WhoisContact())
