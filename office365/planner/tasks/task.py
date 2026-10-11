from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity
from office365.planner.assignments import PlannerAssignments
from office365.planner.tasks.task_details import PlannerTaskDetails
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.planner.assigned_to_task_board_task_format import (
        PlannerAssignedToTaskBoardTaskFormat,
    )
    from office365.planner.bucket_task_board_task_format import (
        PlannerBucketTaskBoardTaskFormat,
    )
    from office365.planner.planner_applied_categories import PlannerAppliedCategories
    from office365.planner.progress_task_board_task_format import (
        PlannerProgressTaskBoardTaskFormat,
    )
    from office365.planner.tasks.previewtype import PlannerPreviewType


class PlannerTask(Entity):
    """
    The plannerTask resource represents a Planner task in Microsoft 365.
    A Planner task is contained in a plan and can be assigned to a bucket in a plan.
    Each task object has a details object which can contain more information about the task.
    See overview for more information regarding relationships between group, plan and task.
    """

    def delete_object(self, *, ignore_missing: bool = False) -> Self:
        def _construct_request(request: RequestOptions) -> None:
            etag = self.properties.get("__etag")
            if etag:
                request.set_header("If-Match", etag)

        super().delete_object(ignore_missing=ignore_missing).before_execute(_construct_request)
        return self

    def update(self) -> Self:
        def _construct_request(request: RequestOptions) -> None:
            etag = self.properties.get("__etag")
            if etag:
                request.set_header("If-Match", etag)

        super().update().before_execute(_construct_request)
        return self

    @odata(name="createdBy")
    @property
    def created_by(self) -> IdentitySet:
        """Identity of the user that created the task."""
        return self.properties.get("createdBy", IdentitySet())

    @odata(name="createdDateTime")
    @property
    def created_datetime(self) -> datetime:
        """
        Date and time at which the task is created.
        """
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def title(self) -> Optional[str]:
        """Required. Title of the task."""
        return self.properties.get("title", None)

    @title.setter
    def title(self, value):
        self.set_property("title", value)

    @property
    def plan_id(self) -> Optional[str]:
        """Required. Name of the bucket."""
        return self.properties.get("planId", None)

    @plan_id.setter
    def plan_id(self, value: str):
        self.set_property("planId", value)

    @property
    def bucket_id(self) -> Optional[str]:
        """Required. Name of the bucket."""
        return self.properties.get("bucketId", None)

    @bucket_id.setter
    def bucket_id(self, value: str):
        self.set_property("bucketId", value)

    @property
    def details(self) -> PlannerTaskDetails:
        """Additional details about the task."""
        return self.properties.get(
            "details",
            PlannerTaskDetails(self.context, ResourcePath("details", self.resource_path)),
        )

    @property
    def percent_complete(self) -> int:
        """Percentage of task completion. 0 = not started, 100 = complete."""
        return self.properties.get("percentComplete", 0)

    @property
    def priority(self) -> int:
        """Priority of the task. 0 = urgent, ..., 5 = medium, 10 = low."""
        return self.properties.get("priority", 5)

    @property
    def assignments(self) -> PlannerAssignments:
        """The set of users assigned to this task (keyed by user ID)."""
        return self.properties.get("assignments", PlannerAssignments())

    @property
    def active_checklist_item_count(self) -> Optional[int]:
        """Gets the activeChecklistItemCount property"""
        return self.properties.get("activeChecklistItemCount", None)

    @property
    def applied_categories(self) -> PlannerAppliedCategories:
        """Gets the appliedCategories property"""
        from office365.planner.planner_applied_categories import (
            PlannerAppliedCategories,
        )

        return self.properties.get("appliedCategories", PlannerAppliedCategories())

    @property
    def assignee_priority(self) -> Optional[str]:
        """Gets the assigneePriority property"""
        return self.properties.get("assigneePriority", None)

    @property
    def checklist_item_count(self) -> Optional[int]:
        """Gets the checklistItemCount property"""
        return self.properties.get("checklistItemCount", None)

    @property
    def completed_by(self) -> IdentitySet:
        """Gets the completedBy property"""
        from office365.directory.identity_set import IdentitySet

        return self.properties.get("completedBy", IdentitySet())

    @property
    def completed_date_time(self) -> Optional[datetime]:
        """Gets the completedDateTime property"""
        return self.properties.get("completedDateTime", datetime.min)

    @property
    def conversation_thread_id(self) -> Optional[str]:
        """Gets the conversationThreadId property"""
        return self.properties.get("conversationThreadId", None)

    @property
    def due_date_time(self) -> Optional[datetime]:
        """Gets the dueDateTime property"""
        return self.properties.get("dueDateTime", datetime.min)

    @property
    def has_description(self) -> Optional[bool]:
        """Gets the hasDescription property"""
        return self.properties.get("hasDescription", None)

    @property
    def order_hint(self) -> Optional[str]:
        """Gets the orderHint property"""
        return self.properties.get("orderHint", None)

    @property
    def preview_type(self) -> PlannerPreviewType:
        """Gets the previewType property"""
        from office365.planner.tasks.previewtype import PlannerPreviewType

        return self.properties.get("previewType", PlannerPreviewType.automatic)

    @property
    def reference_count(self) -> Optional[int]:
        """Gets the referenceCount property"""
        return self.properties.get("referenceCount", None)

    @property
    def start_date_time(self) -> Optional[datetime]:
        """Gets the startDateTime property"""
        return self.properties.get("startDateTime", datetime.min)

    @property
    def assigned_to_task_board_format(self) -> PlannerAssignedToTaskBoardTaskFormat:
        """Gets the assignedToTaskBoardFormat property"""
        from office365.planner.assigned_to_task_board_task_format import (
            PlannerAssignedToTaskBoardTaskFormat,
        )

        return self.properties.get(
            "assignedToTaskBoardFormat",
            PlannerAssignedToTaskBoardTaskFormat(
                self.context, ResourcePath("assignedToTaskBoardFormat", self.resource_path)
            ),
        )

    @property
    def bucket_task_board_format(self) -> PlannerBucketTaskBoardTaskFormat:
        """Gets the bucketTaskBoardFormat property"""
        from office365.planner.bucket_task_board_task_format import (
            PlannerBucketTaskBoardTaskFormat,
        )

        return self.properties.get(
            "bucketTaskBoardFormat",
            PlannerBucketTaskBoardTaskFormat(self.context, ResourcePath("bucketTaskBoardFormat", self.resource_path)),
        )

    @property
    def progress_task_board_format(self) -> PlannerProgressTaskBoardTaskFormat:
        """Gets the progressTaskBoardFormat property"""
        from office365.planner.progress_task_board_task_format import (
            PlannerProgressTaskBoardTaskFormat,
        )

        return self.properties.get(
            "progressTaskBoardFormat",
            PlannerProgressTaskBoardTaskFormat(
                self.context, ResourcePath("progressTaskBoardFormat", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerTask"
