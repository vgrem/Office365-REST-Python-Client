from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.authority_template import AuthorityTemplate
from office365.security.category_template import CategoryTemplate
from office365.security.citation_template import CitationTemplate
from office365.security.department_template import DepartmentTemplate
from office365.security.file_plan_reference_template import (
    FilePlanReferenceTemplate,
)

if TYPE_CHECKING:
    from office365.security.file_plan_applied_category import (
        FilePlanAppliedCategory,
    )
    from office365.security.file_plan_authority import FilePlanAuthority
    from office365.security.file_plan_citation import FilePlanCitation
    from office365.security.file_plan_department import FilePlanDepartment
    from office365.security.file_plan_reference import FilePlanReference


class FilePlanDescriptor(Entity):
    """Represents a file plan descriptor for a retention label."""

    @property
    def authority_template(self) -> AuthorityTemplate:
        """Gets the authorityTemplate property"""
        return self.properties.get(
            "authorityTemplate", AuthorityTemplate(self.context, ResourcePath("authorityTemplate", self.resource_path))
        )

    @property
    def category_template(self) -> CategoryTemplate:
        """Gets the categoryTemplate property"""
        return self.properties.get(
            "categoryTemplate", CategoryTemplate(self.context, ResourcePath("categoryTemplate", self.resource_path))
        )

    @property
    def citation_template(self) -> CitationTemplate:
        """Gets the citationTemplate property"""
        return self.properties.get(
            "citationTemplate", CitationTemplate(self.context, ResourcePath("citationTemplate", self.resource_path))
        )

    @property
    def department_template(self) -> DepartmentTemplate:
        """Gets the departmentTemplate property"""
        return self.properties.get(
            "departmentTemplate",
            DepartmentTemplate(self.context, ResourcePath("departmentTemplate", self.resource_path)),
        )

    @property
    def file_plan_reference_template(self) -> FilePlanReferenceTemplate:
        """Gets the filePlanReferenceTemplate property"""
        return self.properties.get(
            "filePlanReferenceTemplate",
            FilePlanReferenceTemplate(self.context, ResourcePath("filePlanReferenceTemplate", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.FilePlanDescriptor"

    @property
    def authority(self) -> FilePlanAuthority:
        """Gets the authority property"""
        from office365.security.file_plan_authority import FilePlanAuthority

        return self.properties.get("authority", FilePlanAuthority())

    @property
    def category(self) -> FilePlanAppliedCategory:
        """Gets the category property"""
        from office365.security.file_plan_applied_category import (
            FilePlanAppliedCategory,
        )

        return self.properties.get("category", FilePlanAppliedCategory())

    @property
    def citation(self) -> FilePlanCitation:
        """Gets the citation property"""
        from office365.security.file_plan_citation import FilePlanCitation

        return self.properties.get("citation", FilePlanCitation())

    @property
    def department(self) -> FilePlanDepartment:
        """Gets the department property"""
        from office365.security.file_plan_department import FilePlanDepartment

        return self.properties.get("department", FilePlanDepartment())

    @property
    def file_plan_reference(self) -> FilePlanReference:
        """Gets the filePlanReference property"""
        from office365.security.file_plan_reference import FilePlanReference

        return self.properties.get("filePlanReference", FilePlanReference())
