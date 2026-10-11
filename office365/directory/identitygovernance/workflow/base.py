from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.identitygovernance.lifecycleworkflows.category import (
    LifecycleWorkflowCategory,
)
from office365.directory.identitygovernance.task import Task
from office365.directory.identitygovernance.workflow.executionconditions import (
    WorkflowExecutionConditions,
)
from office365.directory.objects.object import DirectoryObject
from office365.directory.users.user import User
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.subject_type import SubjectType


class WorkflowBase(Entity):
    """An abstract type that exposes the properties for configuring a custom lifecycle workflow."""

    @property
    def category(self) -> LifecycleWorkflowCategory:
        """Gets the category property"""
        return self.properties.get("category", LifecycleWorkflowCategory.joiner)

    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def execution_conditions(self) -> WorkflowExecutionConditions:
        """Gets the executionConditions property"""
        return self.properties.get("executionConditions", WorkflowExecutionConditions())

    @property
    def is_enabled(self) -> Optional[bool]:
        """Gets the isEnabled property"""
        return self.properties.get("isEnabled", None)

    @property
    def is_scheduling_enabled(self) -> Optional[bool]:
        """Gets the isSchedulingEnabled property"""
        return self.properties.get("isSchedulingEnabled", None)

    @property
    def last_modified_date_time(self) -> datetime:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def administration_scope_targets(self) -> EntityCollection[DirectoryObject]:
        """Gets the administrationScopeTargets property"""
        return self.properties.get(
            "administrationScopeTargets",
            EntityCollection[DirectoryObject](
                self.context, DirectoryObject, ResourcePath("administrationScopeTargets", self.resource_path)
            ),
        )

    @property
    def created_by(self) -> User:
        """Gets the createdBy property"""
        return self.properties.get("createdBy", User(self.context, ResourcePath("createdBy", self.resource_path)))

    @property
    def last_modified_by(self) -> User:
        """Gets the lastModifiedBy property"""
        return self.properties.get(
            "lastModifiedBy", User(self.context, ResourcePath("lastModifiedBy", self.resource_path))
        )

    @property
    def tasks(self) -> EntityCollection[Task]:
        """Gets the tasks property"""
        return self.properties.get(
            "tasks", EntityCollection[Task](self.context, Task, ResourcePath("tasks", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.identityGovernance.WorkflowBase"

    @property
    def target_subject_type(self) -> SubjectType:
        """Gets the targetSubjectType property"""
        from office365.directory.identitygovernance.subject_type import SubjectType

        return self.properties.get("targetSubjectType", SubjectType.user)
