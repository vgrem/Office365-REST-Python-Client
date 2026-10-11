from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.security.authority_template import AuthorityTemplate
from office365.security.category_template import CategoryTemplate
from office365.security.citation_template import CitationTemplate
from office365.security.department_template import DepartmentTemplate
from office365.security.file_plan_reference_template import FilePlanReferenceTemplate
from office365.security.labels.retention.collection import RetentionLabelCollection


class LabelsRoot(Entity):
    """A root resource for capabilities that support records management for Microsoft 365 data in an organization.

    Those capabilities include using a retention label to configure retention and deletion settings
    for a type of content in the Microsoft 365 data, and using one or more file plan descriptors to supplement
    the retention label and provide additional options to better manage and organize the content.
    """

    @odata(name="retentionLabels")
    @property
    def retention_labels(self) -> RetentionLabelCollection:
        """Represents how customers can manage their data, whether and for how long to retain or delete it."""
        return self.properties.get(
            "retentionLabels",
            RetentionLabelCollection(self.context, ResourcePath("retentionLabels", self.resource_path)),
        )

    @property
    def authorities(self) -> EntityCollection[AuthorityTemplate]:
        """Gets the authorities property"""
        return self.properties.get(
            "authorities",
            EntityCollection[AuthorityTemplate](
                self.context, AuthorityTemplate, ResourcePath("authorities", self.resource_path)
            ),
        )

    @property
    def categories(self) -> EntityCollection[CategoryTemplate]:
        """Gets the categories property"""
        return self.properties.get(
            "categories",
            EntityCollection[CategoryTemplate](
                self.context, CategoryTemplate, ResourcePath("categories", self.resource_path)
            ),
        )

    @property
    def citations(self) -> EntityCollection[CitationTemplate]:
        """Gets the citations property"""
        return self.properties.get(
            "citations",
            EntityCollection[CitationTemplate](
                self.context, CitationTemplate, ResourcePath("citations", self.resource_path)
            ),
        )

    @property
    def departments(self) -> EntityCollection[DepartmentTemplate]:
        """Gets the departments property"""
        return self.properties.get(
            "departments",
            EntityCollection[DepartmentTemplate](
                self.context, DepartmentTemplate, ResourcePath("departments", self.resource_path)
            ),
        )

    @odata(name="filePlanReferences")
    @property
    def file_plan_references(self) -> EntityCollection[FilePlanReferenceTemplate]:
        """Gets the filePlanReferences property"""
        return self.properties.get(
            "filePlanReferences",
            EntityCollection[FilePlanReferenceTemplate](
                self.context, FilePlanReferenceTemplate, ResourcePath("filePlanReferences", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.LabelsRoot"
