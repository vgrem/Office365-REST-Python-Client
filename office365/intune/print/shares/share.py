from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity_collection import EntityCollection
from office365.intune.print.printers.base import PrinterBase
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.groups.group import Group
    from office365.directory.users.user import User
    from office365.intune.print.printers.printer import Printer
    from office365.intune.print.printers.share_viewpoint import PrinterShareViewpoint


class PrinterShare(PrinterBase):
    """Represents a printer that is intended to be discoverable by users and print applications."""

    @property
    def allow_all_users(self) -> Optional[bool]:
        """Gets the allowAllUsers property"""
        return self.properties.get("allowAllUsers", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def view_point(self) -> PrinterShareViewpoint:
        """Gets the viewPoint property"""
        from office365.intune.print.printers.share_viewpoint import PrinterShareViewpoint

        return self.properties.get("viewPoint", PrinterShareViewpoint())

    @property
    def allowed_groups(self) -> EntityCollection[Group]:
        """Gets the allowedGroups property"""
        from office365.directory.groups.group import Group

        return self.properties.get(
            "allowedGroups",
            EntityCollection[Group](self.context, Group, ResourcePath("allowedGroups", self.resource_path)),
        )

    @property
    def allowed_users(self) -> EntityCollection[User]:
        """Gets the allowedUsers property"""
        from office365.directory.users.user import User

        return self.properties.get(
            "allowedUsers", EntityCollection[User](self.context, User, ResourcePath("allowedUsers", self.resource_path))
        )

    @property
    def printer(self) -> Printer:
        """Gets the printer property"""
        from office365.intune.print.printers.printer import Printer

        return self.properties.get("printer", Printer(self.context, ResourcePath("printer", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrinterShare"
