from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, cast

from typing_extensions import Self

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata
from office365.sharepoint.entity import Entity
from office365.sharepoint.listitems.versions.change import SPListItemVersionChange

if TYPE_CHECKING:
    from office365.sharepoint.fields.collection import FieldCollection
    from office365.sharepoint.listitems.versions.collection import (
        ListItemVersionCollection,
    )


class ListItemVersion(Entity):
    """Represents a version of a list item."""

    def __repr__(self):
        return f"Label: {self.version_label}, Url: {self.properties.get('FileRef', None)}"

    @property
    def version_id(self) -> Optional[int]:
        """Gets the ID of the version."""
        return int(self.properties.get("VersionId", -1))

    @property
    def version_label(self) -> Optional[str]:
        """Gets the version number of the item version."""
        return self.properties.get("VersionLabel", None)

    @property
    def is_current_version(self) -> Optional[bool]:
        """Gets a value that specifies whether the file version is the current version."""
        return self.properties.get("IsCurrentVersion", None)

    @property
    def changes(self) -> ClientValueCollection[SPListItemVersionChange]:
        return self.properties.get("Changes", ClientValueCollection(SPListItemVersionChange))

    @property
    def created(self) -> datetime:
        """Gets the creation date and time for the item version."""
        return self.properties.get("Created", datetime.min)

    @property
    def modified(self) -> datetime:
        """Gets the modified date and time for the item version."""
        return self.properties.get("Modified", datetime.min)

    @odata(name="FileVersion")
    @property
    def created_by(self):
        """Gets the user that created the item version."""
        from office365.sharepoint.principal.users.user import User

        return self.properties.get(
            "CreatedBy",
            User(self.context, ResourcePath("CreatedBy", self.resource_path)),
        )

    @property
    def fields(self) -> FieldCollection:
        """Gets the collection of fields that are used in the list that contains the item version."""
        from office365.sharepoint.fields.collection import FieldCollection

        return self.properties.get(
            "Fields",
            FieldCollection(self.context, ResourcePath("Fields", self.resource_path)),
        )

    @odata(name="FileVersion")
    @property
    def file_version(self):
        """"""
        from office365.sharepoint.files.versions.version import FileVersion

        return self.properties.get(
            "FileVersion",
            FileVersion(self.context, ResourcePath("FileVersion", self.resource_path)),
        )

    @property
    def property_ref_name(self):
        return "VersionId"

    @property
    def parent_collection(self) -> ListItemVersionCollection:
        from office365.sharepoint.listitems.versions.collection import (
            ListItemVersionCollection,
        )

        return cast(ListItemVersionCollection, self._parent_collection)

    def recycle(self) -> Self:
        """Recycle operation."""
        qry = ServiceOperationQuery(self, "Recycle", None, {}, None, None)
        self.context.add_query(qry)
        return self
