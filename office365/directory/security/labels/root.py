from office365.directory.security.labels.retention import RetentionLabel
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class LabelsRoot(Entity):
    """A root resource for capabilities that support records management for Microsoft 365 data in an organization.

    Those capabilities include using a retention label to configure retention and deletion settings
    for a type of content in the Microsoft 365 data, and using one or more file plan descriptors to supplement
    the retention label and provide additional options to better manage and organize the content.
    """

    @property
    def retention_labels(self):
        """Represents how customers can manage their data, whether and for how long to retain or delete it."""
        return self.properties.get(
            "retentionLabels",
            EntityCollection(
                self.context,
                RetentionLabel,
                ResourcePath("retentionLabels", self.resource_path),
            ),
        )
