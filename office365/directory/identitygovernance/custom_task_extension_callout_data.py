from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.identitygovernance.task import Task
from office365.directory.identitygovernance.task_processing_result import (
    TaskProcessingResult,
)
from office365.directory.identitygovernance.workflow_subject import WorkflowSubject
from office365.directory.users.user import User
from office365.runtime.client_value import ClientValue


@dataclass
class CustomTaskExtensionCalloutData(ClientValue):
    subject: User | None = None
    task: Task | None = None
    taskProcessingresult: TaskProcessingResult | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.identityGovernance.CustomTaskExtensionCalloutData"

    targetSubject: WorkflowSubject = field(default_factory=WorkflowSubject)
