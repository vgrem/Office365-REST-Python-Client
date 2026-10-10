from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity
from office365.sharepoint.ui.applicationpages.peoplepicker.query_settings import (
    PeoplePickerQuerySettings,
)


class PickerSettings(Entity):
    """
    This class contains configuration settings for the client people picker control hosted
    by the SharePoint sharing UI.
    """

    @property
    def allow_email_addresses(self):
        """
        Boolean value indicating whether the picker control will allow the resolution of arbitrary email addresses.
        """
        return self.properties.get("AllowEmailAddresses", None)

    @property
    def allow_only_email_addresses(self):
        """
        Boolean value indicating whether the picker control will only allow the resolution of email addresses.
        """
        return self.properties.get("AllowOnlyEmailAddresses", None)

    @property
    def query_settings(self):
        """
        The query settings to be used by the picker control.
        """
        return self.properties.get("QuerySettings", PeoplePickerQuerySettings())

    @property
    def principal_account_type(self) -> Optional[str]:
        """Gets the PrincipalAccountType property"""
        return self.properties.get("PrincipalAccountType", None)

    @property
    def principal_source(self) -> Optional[int]:
        """Gets the PrincipalSource property"""
        return self.properties.get("PrincipalSource", None)

    @property
    def use_substrate_search(self) -> Optional[bool]:
        """Gets the UseSubstrateSearch property"""
        return self.properties.get("UseSubstrateSearch", None)

    @property
    def visible_suggestions(self) -> Optional[int]:
        """Gets the VisibleSuggestions property"""
        return self.properties.get("VisibleSuggestions", None)
