from __future__ import annotations

from typing import Optional

from office365.directory.identities.userflows.language_page import UserFlowLanguagePage
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata


class UserFlowLanguageConfiguration(Entity):
    """Allows a user flow to support the use of multiple languages.

    For Azure Active Directory user flows, you can only leverage the built-in languages provided by Microsoft.
    User flows for Azure Active Directory support defining the language and strings shown to users
    as they go through the journeys you configure with your user flows."""

    def __str__(self):
        return self.display_name or self.entity_type_name

    @property
    def display_name(self) -> Optional[str]:
        """The language name to display."""
        return self.properties.get("displayName", None)

    @odata(name="defaultPages")
    @property
    def default_pages(self) -> EntityCollection[UserFlowLanguagePage]:
        """Collection of pages with the default content to display in a user flow for a specified language."""
        return self.properties.get(
            "defaultPages",
            EntityCollection(
                self.context,
                UserFlowLanguagePage,
                ResourcePath("defaultPages", self.resource_path),
            ),
        )

    @odata(name="overridesPages")
    @property
    def overrides_pages(self) -> EntityCollection[UserFlowLanguagePage]:
        """Collection of pages with the default content to display in a user flow for a specified language."""
        return self.properties.get(
            "overridesPages",
            EntityCollection(
                self.context,
                UserFlowLanguagePage,
                ResourcePath("overridesPages", self.resource_path),
            ),
        )

    @property
    def is_enabled(self) -> Optional[bool]:
        """Gets the isEnabled property"""
        return self.properties.get("isEnabled", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserFlowLanguageConfiguration"
