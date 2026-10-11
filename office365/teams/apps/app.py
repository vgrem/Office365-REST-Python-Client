from __future__ import annotations

from typing import Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.teams.apps.definition import TeamsAppDefinition


class TeamsApp(Entity):
    """Represents an app in the Microsoft Teams app catalog."""

    def __str__(self):
        return self.display_name or self.entity_type_name

    @property
    def display_name(self) -> str | None:
        """The title of the TeamsApp."""
        return self.properties.get("displayName")

    @property
    def distribution_method(self) -> str | None:
        """The title of the TeamsApp."""
        return self.properties.get("distributionMethod")

    @odata(name="appDefinitions")
    @property
    def app_definitions(self) -> EntityCollection[TeamsAppDefinition]:
        """The details for each version of the app."""
        return self.properties.get(
            "appDefinitions",
            EntityCollection(
                self.context,
                TeamsAppDefinition,
                ResourcePath("appDefinitions", self.resource_path),
            ),
        )

    @property
    def external_id(self) -> Optional[str]:
        """Gets the externalId property"""
        return self.properties.get("externalId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TeamsApp"
