from __future__ import annotations

from typing import Any, Dict, Optional

from office365.runtime.converters.keyvalue import parse_key_value_collection
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata
from office365.sharepoint.entity import Entity


class PersonProperties(Entity):
    """
    The PersonProperties class contains the data about people and is returned by PeopleManager methods
    (see section 3.1.5.58).
    """

    def __str__(self):
        return self.display_name or self.entity_type_name

    @property
    def account_name(self) -> Optional[str]:
        """The AccountName property specifies the person's account name."""
        return self.properties.get("AccountName", None)

    @property
    def display_name(self) -> Optional[str]:
        """The DisplayName property specifies the person's display name."""
        return self.properties.get("DisplayName", None)

    @property
    def email(self) -> Optional[str]:
        """The Email property specifies the person's email address."""
        return self.properties.get("Email", None)

    @property
    def latest_post(self) -> Optional[str]:
        """The  LatestPost property specifies the person's latest microblog post."""
        return self.properties.get("LatestPost", None)

    @property
    def peers(self) -> StringCollection:
        """
        The Peers property specifies an array of strings that specify the account names of person's peers, that is,
        those who have the same manager.
        """
        return self.properties.get("Peers", StringCollection())

    @property
    def personal_url(self) -> Optional[str]:
        """The PersonalUrl property specifies the absolute URL of the person's personal page."""
        return self.properties.get("PersonalUrl", None)

    @odata(name="ExtendedManagers")
    @property
    def extended_managers(self) -> StringCollection:
        """
        The ExtendedManagers property specifies an array of strings that specify the account names of
        a person's managers.
        """
        return self.properties.get("ExtendedManagers", StringCollection())

    @odata(name="ExtendedReports")
    @property
    def extended_reports(self) -> StringCollection:
        """
        The ExtendedReports properties specifies an array of strings that specify the account names of
        person's extended reports.
        """
        return self.properties.get("ExtendedReports", StringCollection())

    @property
    def picture_url(self) -> Optional[str]:
        """The PictureUrl property specifies the  URL for the person's profile picture."""
        return self.properties.get("PictureUrl", None)

    @property
    def user_url(self) -> Optional[str]:
        """The UserUrl property specifies the URL for the person's profile."""
        return self.properties.get("UserUrl", None)

    @property
    def user_profile_properties(self) -> Optional[Dict[str, Any]]:
        """"""
        return self.properties.get("UserProfileProperties", None)

    @property
    def entity_type_name(self):
        return "SP.UserProfiles.PersonProperties"

    def set_property(self, k, v, persist_changes=True):  # type: ignore[override]
        if k == "UserProfileProperties":
            v = parse_key_value_collection(v)
        super().set_property(k, v)
        return self

    @property
    def direct_reports(self) -> StringCollection:
        """Gets the DirectReports property"""
        return self.properties.get("DirectReports", StringCollection())

    @property
    def is_followed(self) -> Optional[bool]:
        """Gets the IsFollowed property"""
        return self.properties.get("IsFollowed", None)

    @property
    def personal_site_host_url(self) -> Optional[str]:
        """Gets the PersonalSiteHostUrl property"""
        return self.properties.get("PersonalSiteHostUrl", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)
