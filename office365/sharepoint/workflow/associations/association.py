from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class WorkflowAssociation(Entity):
    """Represents the association of a workflow template with a specific list or content type"""

    @property
    def allow_manual(self) -> Optional[bool]:
        """Gets the AllowManual property"""
        return self.properties.get("AllowManual", None)

    @property
    def association_data(self) -> Optional[str]:
        """Gets the AssociationData property"""
        return self.properties.get("AssociationData", None)

    @property
    def auto_start_change(self) -> Optional[bool]:
        """Gets the AutoStartChange property"""
        return self.properties.get("AutoStartChange", None)

    @property
    def auto_start_create(self) -> Optional[bool]:
        """Gets the AutoStartCreate property"""
        return self.properties.get("AutoStartCreate", None)

    @property
    def base_id(self) -> Optional[UUID]:
        """Gets the BaseId property"""
        return self.properties.get("BaseId", None)

    @property
    def created(self) -> datetime | None:
        """Gets the Created property"""
        return self.properties.get("Created", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)

    @property
    def enabled(self) -> Optional[bool]:
        """Gets the Enabled property"""
        return self.properties.get("Enabled", None)

    @property
    def history_list_title(self) -> Optional[str]:
        """Gets the HistoryListTitle property"""
        return self.properties.get("HistoryListTitle", None)

    @property
    def instantiation_url(self) -> Optional[str]:
        """Gets the InstantiationUrl property"""
        return self.properties.get("InstantiationUrl", None)

    @property
    def internal_name(self) -> Optional[str]:
        """Gets the InternalName property"""
        return self.properties.get("InternalName", None)

    @property
    def is_declarative(self) -> Optional[bool]:
        """Gets the IsDeclarative property"""
        return self.properties.get("IsDeclarative", None)

    @property
    def list_id(self) -> Optional[UUID]:
        """Gets the ListId property"""
        return self.properties.get("ListId", None)

    @property
    def modified(self) -> datetime | None:
        """Gets the Modified property"""
        return self.properties.get("Modified", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the Name property"""
        return self.properties.get("Name", None)

    @property
    def running_instances(self) -> Optional[int]:
        """Gets the RunningInstances property"""
        return self.properties.get("RunningInstances", None)

    @property
    def task_list_title(self) -> Optional[str]:
        """Gets the TaskListTitle property"""
        return self.properties.get("TaskListTitle", None)

    @property
    def web_id(self) -> Optional[UUID]:
        """Gets the WebId property"""
        return self.properties.get("WebId", None)

    @property
    def entity_type_name(self):
        return "SP.Workflow.WorkflowAssociation"

    @property
    def id(self) -> Optional[UUID]:
        """Gets the Id property"""
        return self.properties.get("Id", None)
