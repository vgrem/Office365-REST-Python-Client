from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.admin.baseline_parameter import BaselineParameter
    from office365.admin.baseline_resource import BaselineResource


class ConfigurationBaseline(Entity):
    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def parameters(self) -> ClientValueCollection[BaselineParameter]:
        """Gets the parameters property"""
        from office365.admin.baseline_parameter import BaselineParameter

        return self.properties.get("parameters", ClientValueCollection[BaselineParameter](BaselineParameter))

    @property
    def resources(self) -> ClientValueCollection[BaselineResource]:
        """Gets the resources property"""
        from office365.admin.baseline_resource import BaselineResource

        return self.properties.get("resources", ClientValueCollection[BaselineResource](BaselineResource))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ConfigurationBaseline"
