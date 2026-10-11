from __future__ import annotations

from typing import Optional

from office365.entity_collection import EntityCollection
from office365.onedrive.driveitems.driveItem import DriveItem
from office365.runtime.http.prefer import TRY_FILTER_LAST_MODIFIED_DATE_TIME
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.query_capabilities import query_capabilities

_DOC = "https://learn.microsoft.com/en-us/graph/known-issues"


@query_capabilities(
    unsupported_filter={"size"},
    prefer={"lastModifiedDateTime": TRY_FILTER_LAST_MODIFIED_DATE_TIME},
    doc=_DOC,
    note="driveItem.size maps to SharePoint's SMTotalFileStreamSize, which the service won't filter",
)
class DriveItemCollection(EntityCollection[DriveItem]):
    """A collection of :class:`~office365.onedrive.driveitems.driveItem.DriveItem` resources.

    The endpoint accepts the usual OData query options with two caveats, declared
    above: ``$filter`` cannot reference ``size`` (``order_by("size")`` is fine),
    and filtering ``lastModifiedDateTime`` requires a ``Prefer`` header the
    collection adds automatically.
    """

    def __init__(self, context, resource_path: Optional[ResourcePath] = None):
        super().__init__(context, DriveItem, resource_path)
