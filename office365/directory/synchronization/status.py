from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.directory.synchronization.progress import SynchronizationProgress
from office365.directory.synchronization.quarantine import SynchronizationQuarantine
from office365.directory.synchronization.statuscode import SynchronizationStatusCode
from office365.directory.synchronization.task_execution import SynchronizationTaskExecution
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.string_key_long_value_pair import StringKeyLongValuePair


@dataclass
class SynchronizationStatus(ClientValue):
    """Represents the current status of the synchronizationJob."""

    progress: ClientValueCollection[SynchronizationProgress] = field(
        default_factory=lambda: ClientValueCollection(SynchronizationProgress)
    )
    quarantine: SynchronizationQuarantine = field(default_factory=SynchronizationQuarantine)
    lastExecution: SynchronizationTaskExecution = field(default_factory=SynchronizationTaskExecution)
    lastSuccessfulExecution: SynchronizationTaskExecution = field(default_factory=SynchronizationTaskExecution)
    lastSuccessfulExecutionWithExports: SynchronizationTaskExecution = field(
        default_factory=SynchronizationTaskExecution
    )
    code: SynchronizationStatusCode = SynchronizationStatusCode.NotConfigured
    countSuccessiveCompleteFailures: int | None = None
    escrowsPruned: bool | None = None
    steadyStateFirstAchievedTime: datetime | None = field(default_factory=lambda: datetime.min)
    steadyStateLastAchievedTime: datetime | None = field(default_factory=lambda: datetime.min)
    synchronizedEntryCountByType: ClientValueCollection[StringKeyLongValuePair] = field(
        default_factory=lambda: ClientValueCollection(StringKeyLongValuePair)
    )
    troubleshootingUrl: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SynchronizationStatus"
