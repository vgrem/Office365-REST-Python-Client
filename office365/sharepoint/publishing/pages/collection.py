from typing import Optional

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.deprecated import deprecated
from office365.runtime.odata.literals import escape_odata_string
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.publishing.pages.metadata_collection import (
    SitePageMetadataCollection,
)
from office365.sharepoint.publishing.pages.page import SitePage
from office365.sharepoint.translation.status_collection import (
    TranslationStatusCollection,
)


class SitePageCollection(SitePageMetadataCollection[SitePage]):
    def __init__(self, context, resource_path=None):
        """Specifies a collection of site pages."""
        if resource_path is None:
            resource_path = ResourcePath("SP.Publishing.SitePageCollection")
        super().__init__(context, SitePage, resource_path)

    def add(
        self,
        name: Optional[str] = None,
        title: Optional[str] = None,
        page_layout_type: Optional[str] = None,
    ) -> SitePage:
        """Adds (creates a draft) site page.

        Args:
            name: The page file name, e.g. ``Home.aspx``. The server rejects a
                create that does not name the page.
            title: The page title; defaults to ``name``.
            page_layout_type: The page layout, e.g. ``Article`` (the modern page
                default) or ``SingleWebPartAppPage``.
        """
        return_type = SitePage(self.context)
        if name is not None:
            return_type.set_property("Name", name)
        return_type.set_property("Title", title or name or "", True)
        if page_layout_type is not None:
            return_type.set_property("PageLayoutType", page_layout_type)
        qry = CreateEntityQuery(self, return_type, return_type)
        self.context.add_query(qry)
        self.add_child(return_type)
        return return_type

    def create_app_page(self, web_part_data: Optional[str] = None) -> ClientResult[str]:
        """Args:
        web_part_data (str):
        """
        return_type = ClientResult(self.context)
        payload = {"webPartDataAsJson": web_part_data}
        qry = ServiceOperationQuery(self, "CreateAppPage", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_translations(self, source_item_id=None):
        """Args:
        source_item_id (str):
        """
        return_type = TranslationStatusCollection(self.context)
        qry = ServiceOperationQuery(self, "GetTranslations", [source_item_id], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def is_site_page(self, url: str) -> ClientResult[bool]:
        """Indicates whether a specific item is a modern site page.

        Args:
            url (str): URL of the SitePage to be checked.
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "IsSitePage", [url], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_page_column_state(self, url: str) -> ClientResult[int]:
        """Determines whether a specific SitePage is a single or multicolumn page.

        Args:
            url (str): URL of the SitePage for which to return state.
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "GetPageColumnState", [url], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_by_url(self, url: str) -> SitePage:
        """Gets the site page with the specified server relative url.

        Args:
            url (str): Specifies the server relative url of the site page.
        """
        return SitePage(self.context, ServiceOperationPath("GetByUrl", [url], self.resource_path))

    def find_by_name(self, name: str, *, required: bool = False) -> SitePage:
        """Look up the site page with the specified file name.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        page matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            name (str): Specifies the name of the site page.
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"FileName eq '{escape_odata_string(name)}'", required=required)

    @deprecated("Use find_by_name() instead.", version="4.0")
    def get_by_name(self, name: str) -> SitePage:
        """Deprecated alias of :meth:`find_by_name` (strict).

        Args:
            name (str): Specifies the name of the site page.
        """
        return self.find_by_name(name, required=True)

    def templates(self):
        """"""
        return SitePageMetadataCollection(
            self.context,
            SitePage,
            ServiceOperationPath("Templates", None, self.resource_path),
        )

    def update_full_page_app(self, server_relative_url: str, web_part_data_as_json: str) -> Self:
        """Args:
        server_relative_url (str):
        web_part_data_as_json (str):
        """
        payload = {
            "serverRelativeUrl": server_relative_url,
            "webPartDataAsJson": web_part_data_as_json,
        }
        qry = ServiceOperationQuery(self, "UpdateFullPageApp", None, payload)
        self.context.add_query(qry)
        return self
