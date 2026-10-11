from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.directory.profile_source_localization import (
        ProfileSourceLocalization,
    )


class ProfileSource(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def kind(self) -> Optional[str]:
        """Gets the kind property"""
        return self.properties.get("kind", None)

    @property
    def localizations(self) -> ClientValueCollection[ProfileSourceLocalization]:
        """Gets the localizations property"""
        from office365.directory.profile_source_localization import (
            ProfileSourceLocalization,
        )

        return self.properties.get(
            "localizations", ClientValueCollection[ProfileSourceLocalization](ProfileSourceLocalization)
        )

    @property
    def source_id(self) -> Optional[str]:
        """Gets the sourceId property"""
        return self.properties.get("sourceId", None)

    @property
    def web_url(self) -> Optional[str]:
        """Gets the webUrl property"""
        return self.properties.get("webUrl", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProfileSource"
