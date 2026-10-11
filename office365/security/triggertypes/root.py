from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.triggertypes.collection import (
    RetentionEventTypeCollection,
)


class TriggerTypesRoot(Entity):
    """"""

    @property
    def retention_event_types(self) -> RetentionEventTypeCollection:
        """Represents the retentionEventType objects and their properties."""
        return self.properties.get(
            "retentionEventTypes",
            RetentionEventTypeCollection(
                self.context,
                ResourcePath("retentionEventTypes", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.triggerTypesRoot"
