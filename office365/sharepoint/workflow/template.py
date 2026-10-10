from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity
from office365.sharepoint.permissions.base_permissions import BasePermissions


class WorkflowTemplate(Entity):
    """Represents a workflow template currently deployed on the site"""

    @property
    def allow_manual(self) -> Optional[bool]:
        """Gets the AllowManual property"""
        return self.properties.get("AllowManual", None)

    @property
    def association_url(self) -> Optional[str]:
        """Gets the AssociationUrl property"""
        return self.properties.get("AssociationUrl", None)

    @property
    def auto_start_change(self) -> Optional[bool]:
        """Gets the AutoStartChange property"""
        return self.properties.get("AutoStartChange", None)

    @property
    def auto_start_create(self) -> Optional[bool]:
        """Gets the AutoStartCreate property"""
        return self.properties.get("AutoStartCreate", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)

    @property
    def is_declarative(self) -> Optional[bool]:
        """Gets the IsDeclarative property"""
        return self.properties.get("IsDeclarative", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the Name property"""
        return self.properties.get("Name", None)

    @property
    def permissions_manual(self) -> BasePermissions:
        """Gets the PermissionsManual property"""
        return self.properties.get("PermissionsManual", BasePermissions())

    @property
    def entity_type_name(self):
        return "SP.Workflow.WorkflowTemplate"

    @property
    def id(self) -> Optional[UUID]:
        """Gets the Id property"""
        return self.properties.get("Id", None)
