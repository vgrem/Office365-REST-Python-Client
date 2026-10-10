from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.directory.identitygovernance.quarantine_details import QuarantineDetails
from office365.directory.identitygovernance.run import Run
from office365.directory.identitygovernance.task_report import TaskReport
from office365.directory.identitygovernance.user_processing_result import UserProcessingResult
from office365.directory.identitygovernance.workflow_setting import WorkflowSetting
from office365.directory.identitygovernance.workflow_version import WorkflowVersion
from office365.directory.objects.object import DirectoryObject
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class Workflow(Entity):
    @property
    def deleted_date_time(self) -> Optional[datetime]:
        """Gets the deletedDateTime property"""
        return self.properties.get("deletedDateTime", datetime.min)

    @property
    def id_(self) -> Optional[str]:
        """Gets the id property"""
        return self.properties.get("id", None)

    @property
    def next_schedule_run_date_time(self) -> Optional[datetime]:
        """Gets the nextScheduleRunDateTime property"""
        return self.properties.get("nextScheduleRunDateTime", datetime.min)

    @property
    def quarantine_details(self) -> QuarantineDetails:
        """Gets the quarantineDetails property"""
        return self.properties.get("quarantineDetails", QuarantineDetails())

    @property
    def settings(self) -> WorkflowSetting:
        """Gets the settings property"""
        return self.properties.get("settings", WorkflowSetting())

    @property
    def version(self) -> Optional[int]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def execution_scope(self) -> EntityCollection[UserProcessingResult]:
        """Gets the executionScope property"""
        return self.properties.get(
            "executionScope",
            EntityCollection[UserProcessingResult](
                self.context, UserProcessingResult, ResourcePath("executionScope", self.resource_path)
            ),
        )

    @property
    def preview_scope(self) -> EntityCollection[DirectoryObject]:
        """Gets the previewScope property"""
        return self.properties.get(
            "previewScope",
            EntityCollection[DirectoryObject](
                self.context, DirectoryObject, ResourcePath("previewScope", self.resource_path)
            ),
        )

    @property
    def runs(self) -> EntityCollection[Run]:
        """Gets the runs property"""
        return self.properties.get(
            "runs", EntityCollection[Run](self.context, Run, ResourcePath("runs", self.resource_path))
        )

    @property
    def task_reports(self) -> EntityCollection[TaskReport]:
        """Gets the taskReports property"""
        return self.properties.get(
            "taskReports",
            EntityCollection[TaskReport](self.context, TaskReport, ResourcePath("taskReports", self.resource_path)),
        )

    @property
    def user_processing_results(self) -> EntityCollection[UserProcessingResult]:
        """Gets the userProcessingResults property"""
        return self.properties.get(
            "userProcessingResults",
            EntityCollection[UserProcessingResult](
                self.context, UserProcessingResult, ResourcePath("userProcessingResults", self.resource_path)
            ),
        )

    @property
    def versions(self) -> EntityCollection[WorkflowVersion]:
        """Gets the versions property"""
        return self.properties.get(
            "versions",
            EntityCollection[WorkflowVersion](
                self.context, WorkflowVersion, ResourcePath("versions", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.identityGovernance.Workflow"
