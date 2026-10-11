from typing import Optional

from office365.entity_collection import EntityCollection
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.security.labels.retention.actionafterretentionperiod import (
    ActionAfterRetentionPeriod,
)
from office365.security.labels.retention.behaviorduringretentionperiod import (
    BehaviorDuringRetentionPeriod,
)
from office365.security.labels.retention.defaultrecordbehavior import (
    DefaultRecordBehavior,
)
from office365.security.labels.retention.duration import RetentionDuration
from office365.security.labels.retention.label import RetentionLabel
from office365.security.labels.retention.trigger import RetentionTrigger


class RetentionLabelCollection(EntityCollection[RetentionLabel]):
    """"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, RetentionLabel, resource_path)

    def add(
        self,
        display_name: str,
        retention_trigger: RetentionTrigger,
        retention_duration: RetentionDuration,
        behavior_during_retention_period: BehaviorDuringRetentionPeriod,
        default_record_behavior: DefaultRecordBehavior,
        action_after_retention_period: ActionAfterRetentionPeriod,
        description_for_admins: Optional[str] = None,
        description_for_users: Optional[str] = None,
        label_to_be_applied: Optional[str] = None,
    ):
        """
        Create a new retentionLabel object.

        To create a disposition review stage, include the actionAfterRetentionPeriod property in the request body
        with one of the possible values specified.
        """

        def _construct_request(request: RequestOptions) -> None:
            request.set_header("Content-Type", "application/json")

        payload = dict(
            displayName=display_name,
            retentionTrigger=retention_trigger.name,
            retentionDuration=retention_duration,
            behaviorDuringRetentionPeriod=behavior_during_retention_period.name,
            defaultRecordBehavior=default_record_behavior.name,
            actionAfterRetentionPeriod=action_after_retention_period.name,
        )
        if description_for_admins is not None:
            payload["descriptionForAdmins"] = description_for_admins
        if description_for_users is not None:
            payload["descriptionForUsers"] = description_for_users
        if label_to_be_applied is not None:
            payload["labelToBeApplied"] = label_to_be_applied

        return_type = RetentionLabel(self.context, EntityPath(None, self.resource_path))
        self.add_child(return_type)
        qry = CreateEntityQuery(self, payload, return_type)
        self.context.add_query(qry)
        return return_type
