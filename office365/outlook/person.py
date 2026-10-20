from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.booking.phone import Phone
from office365.entity import Entity
from office365.outlook.mail.location import Location
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.onedrive.sites.website import Website
    from office365.outlook.people.person_type import PersonType
    from office365.outlook.scored_email_address import ScoredEmailAddress


class Person(Entity):
    """Represents an aggregation of information about a person from across mail and contacts.
    People can be local contacts or your organization's directory, and people from recent communications
    (such as email)."""

    @odata(name="birthday")
    @property
    def birthday(self) -> Optional[str]:
        """Gets the birthday property"""
        return self.properties.get("birthday", None)

    @odata(name="companyName")
    @property
    def company_name(self) -> Optional[str]:
        """Gets the companyName property"""
        return self.properties.get("companyName", None)

    @odata(name="department")
    @property
    def department(self) -> Optional[str]:
        """Gets the department property"""
        return self.properties.get("department", None)

    @odata(name="displayName")
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @odata(name="givenName")
    @property
    def given_name(self) -> Optional[str]:
        """Gets the givenName property"""
        return self.properties.get("givenName", None)

    @odata(name="imAddress")
    @property
    def im_address(self) -> Optional[str]:
        """Gets the imAddress property"""
        return self.properties.get("imAddress", None)

    @odata(name="isFavorite")
    @property
    def is_favorite(self) -> Optional[bool]:
        """Gets the isFavorite property"""
        return self.properties.get("isFavorite", None)

    @odata(name="jobTitle")
    @property
    def job_title(self) -> Optional[str]:
        """Gets the jobTitle property"""
        return self.properties.get("jobTitle", None)

    @odata(name="officeLocation")
    @property
    def office_location(self) -> Optional[str]:
        """Gets the officeLocation property"""
        return self.properties.get("officeLocation", None)

    @odata(name="personNotes")
    @property
    def person_notes(self) -> Optional[str]:
        """Gets the personNotes property"""
        return self.properties.get("personNotes", None)

    @odata(name="phones")
    @property
    def phones(self) -> ClientValueCollection[Phone]:
        """Gets the phones property"""
        return self.properties.get("phones", ClientValueCollection[Phone](Phone))

    @odata(name="postalAddresses")
    @property
    def postal_addresses(self) -> ClientValueCollection[Location]:
        """Gets the postalAddresses property"""
        return self.properties.get("postalAddresses", ClientValueCollection[Location](Location))

    @odata(name="profession")
    @property
    def profession(self) -> Optional[str]:
        """Gets the profession property"""
        return self.properties.get("profession", None)

    @odata(name="surname")
    @property
    def surname(self) -> Optional[str]:
        """Gets the surname property"""
        return self.properties.get("surname", None)

    @odata(name="userPrincipalName")
    @property
    def user_principal_name(self) -> Optional[str]:
        """Gets the userPrincipalName property"""
        return self.properties.get("userPrincipalName", None)

    @odata(name="yomiCompany")
    @property
    def yomi_company(self) -> Optional[str]:
        """Gets the yomiCompany property"""
        return self.properties.get("yomiCompany", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Person"

    @odata(name="personType")
    @property
    def person_type(self) -> PersonType:
        """Gets the personType property"""
        from office365.outlook.people.person_type import PersonType

        return self.properties.get("personType", PersonType())

    @odata(name="scoredEmailAddresses")
    @property
    def scored_email_addresses(self) -> ClientValueCollection[ScoredEmailAddress]:
        """Gets the scoredEmailAddresses property"""
        from office365.outlook.scored_email_address import ScoredEmailAddress

        return self.properties.get("scoredEmailAddresses", ClientValueCollection[ScoredEmailAddress](ScoredEmailAddress))

    @odata(name="websites")
    @property
    def websites(self) -> ClientValueCollection[Website]:
        """Gets the websites property"""
        from office365.onedrive.sites.website import Website

        return self.properties.get("websites", ClientValueCollection[Website](Website))
