from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.lifecycleworkflowprocessingstatus import (
        LifecycleWorkflowProcessingStatus,
    )
    from office365.directory.identitygovernance.run import Run
    from office365.directory.identitygovernance.subject_type import SubjectType
    from office365.directory.identitygovernance.task_processing_result import (
        TaskProcessingResult,
    )
    from office365.directory.identitygovernance.workflow.executiontype import (
        WorkflowExecutionType,
    )
    from office365.directory.identitygovernance.workflow.subject import WorkflowSubject


class SubjectProcessingResult(Entity):
    @property
    def completed_date_time(self) -> Optional[datetime]:
        """Gets the completedDateTime property"""
        return self.properties.get("completedDateTime", datetime.min)

    @property
    def failed_tasks_count(self) -> Optional[int]:
        """Gets the failedTasksCount property"""
        return self.properties.get("failedTasksCount", None)

    @property
    def processing_status(self) -> LifecycleWorkflowProcessingStatus:
        """Gets the processingStatus property"""
        from office365.directory.identitygovernance.lifecycleworkflowprocessingstatus import (
            LifecycleWorkflowProcessingStatus,
        )

        return self.properties.get("processingStatus", LifecycleWorkflowProcessingStatus.queued)

    @property
    def scheduled_date_time(self) -> Optional[datetime]:
        """Gets the scheduledDateTime property"""
        return self.properties.get("scheduledDateTime", datetime.min)

    @property
    def started_date_time(self) -> Optional[datetime]:
        """Gets the startedDateTime property"""
        return self.properties.get("startedDateTime", datetime.min)

    @property
    def subject(self) -> WorkflowSubject:
        """Gets the subject property"""
        from office365.directory.identitygovernance.workflow.subject import (
            WorkflowSubject,
        )

        return self.properties.get("subject", WorkflowSubject())

    @property
    def subject_type(self) -> SubjectType:
        """Gets the subjectType property"""
        from office365.directory.identitygovernance.subject_type import SubjectType

        return self.properties.get("subjectType", SubjectType.user)

    @property
    def total_tasks_count(self) -> Optional[int]:
        """Gets the totalTasksCount property"""
        return self.properties.get("totalTasksCount", None)

    @property
    def total_unprocessed_tasks_count(self) -> Optional[int]:
        """Gets the totalUnprocessedTasksCount property"""
        return self.properties.get("totalUnprocessedTasksCount", None)

    @property
    def workflow_execution_type(self) -> WorkflowExecutionType:
        """Gets the workflowExecutionType property"""
        from office365.directory.identitygovernance.workflow.executiontype import (
            WorkflowExecutionType,
        )

        return self.properties.get("workflowExecutionType", WorkflowExecutionType.scheduled)

    @property
    def workflow_version(self) -> Optional[int]:
        """Gets the workflowVersion property"""
        return self.properties.get("workflowVersion", None)

    @property
    def reprocessed_runs(self) -> EntityCollection[Run]:
        """Gets the reprocessedRuns property"""
        from office365.directory.identitygovernance.run import Run

        return self.properties.get(
            "reprocessedRuns",
            EntityCollection[Run](self.context, Run, ResourcePath("reprocessedRuns", self.resource_path)),
        )

    @property
    def task_processing_results(self) -> EntityCollection[TaskProcessingResult]:
        """Gets the taskProcessingResults property"""
        from office365.directory.identitygovernance.task_processing_result import (
            TaskProcessingResult,
        )

        return self.properties.get(
            "taskProcessingResults",
            EntityCollection[TaskProcessingResult](
                self.context, TaskProcessingResult, ResourcePath("taskProcessingResults", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.identityGovernance.SubjectProcessingResult"
