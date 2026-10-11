from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity_collection import EntityCollection
from office365.onedrive.sitepages.site_page import SitePage
from office365.onedrive.sitepages.title_area import TitleArea
from office365.runtime.deprecated import deprecated
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.literals import escape_odata_string
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.graph_client import GraphClient
    from office365.onedrive.lists.list import List


class SitePageCollection(EntityCollection[SitePage]):
    """Sites container"""

    def __init__(
        self,
        context: GraphClient,
        resource_path: ResourcePath | None = None,
        parent_list: List | None = None,
    ) -> None:
        super().__init__(context, SitePage, resource_path, parent_list)

    def find_by_name(self, name: str, *, required: bool = False) -> SitePage:
        """Look up a site page by its ``name``.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        page matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            name (str): The site page name
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"name eq '{escape_odata_string(name)}'", required=required)

    def find_by_title(self, title: str, *, required: bool = False) -> SitePage:
        """Look up a site page by its ``title``.

        Deferred — run with ``execute_query()``. Tolerant by default; pass
        ``required=True`` to raise on a missing or ambiguous match.

        Args:
            title (str): The site page title
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"title eq '{escape_odata_string(title)}'", required=required)

    @deprecated("Use find_by_name() instead.", version="4.0")
    def get_by_name(self, name: str) -> SitePage:
        """Deprecated alias of :meth:`find_by_name` (strict)."""
        return self.find_by_name(name, required=True)

    @deprecated("Use find_by_title() instead.", version="4.0")
    def get_by_title(self, title: str) -> SitePage:
        """Deprecated alias of :meth:`find_by_title` (strict)."""
        return self.find_by_title(title, required=True)

    def add(self, title: str, page_layout: str = "article"):
        """Create a new sitePage in the site pages list in a site.

        Args:
            title (str):
            page_layout (str):
        """

        def _construct_request(request: RequestOptions) -> None:
            request.set_header("Content-Type", "application/json")

        return (
            super()
            .add(
                title=title,
                name=f"{title}.aspx",
                pageLayout=page_layout,
                titleArea=TitleArea(),
            )
            .before_execute(_construct_request)
        )
