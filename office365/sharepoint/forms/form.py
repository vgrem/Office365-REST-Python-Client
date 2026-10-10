from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath


class Form(Entity):
    """A form provides a display and editing interface for a single list item."""

    @property
    def form_type(self) -> Optional[str]:
        """
        Gets the type of the form.
        """
        return self.properties.get("FormType", None)

    @property
    def server_relative_url(self) -> Optional[str]:
        """
        Gets the server-relative URL of the form.
        """
        return self.properties.get("ServerRelativeUrl", None)

    @property
    def resource_path(self) -> SPResPath:  # type: ignore[override]
        """
        Gets the Web site–relative Path of the form
        """
        return self.properties.get("ResourcePath", SPResPath())

    @property
    def id(self) -> Optional[UUID]:
        """Gets the Id property"""
        return self.properties.get("Id", None)
