from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.identitygovernance.lifecycleworkflowprocessingstatus import LifecycleWorkflowProcessingStatus
from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class AwaitedWorkflowProcessingResult(ClientValue):
    processingStatus: LifecycleWorkflowProcessingStatus = LifecycleWorkflowProcessingStatus.queued
    statusReasons: StringCollection = field(default_factory=StringCollection)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.identityGovernance.AwaitedWorkflowProcessingResult"
