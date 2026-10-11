from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.synchronization.on_premises_directory_synchronization_configuration import (
        OnPremisesDirectorySynchronizationConfiguration,
    )
    from office365.directory.synchronization.on_premises_directory_synchronization_feature import (
        OnPremisesDirectorySynchronizationFeature,
    )


class OnPremisesDirectorySynchronization(Entity):
    @property
    def configuration(self) -> OnPremisesDirectorySynchronizationConfiguration:
        """Gets the configuration property"""
        from office365.directory.synchronization.on_premises_directory_synchronization_configuration import (
            OnPremisesDirectorySynchronizationConfiguration,
        )

        return self.properties.get("configuration", OnPremisesDirectorySynchronizationConfiguration())

    @property
    def features(self) -> OnPremisesDirectorySynchronizationFeature:
        """Gets the features property"""
        from office365.directory.synchronization.on_premises_directory_synchronization_feature import (
            OnPremisesDirectorySynchronizationFeature,
        )

        return self.properties.get("features", OnPremisesDirectorySynchronizationFeature())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnPremisesDirectorySynchronization"
