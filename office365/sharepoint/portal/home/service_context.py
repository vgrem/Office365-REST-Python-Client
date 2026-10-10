from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.oauth.token_response import TokenResponse
    from office365.sharepoint.portal.home.datacachecollection import (
        SharePointHomeDataCacheCollection,
    )
    from office365.sharepoint.portal.home.page_context import SharePointHomePageContext


class SharePointHomeServiceContext(Entity):
    """
    This data type is reserved for future use and MUST NOT be used by the protocol implementation.
    """

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Portal.SharePointHomeServiceContext"

    @property
    def home_page_cache(self) -> SharePointHomeDataCacheCollection:
        """Gets the HomePageCache property"""
        from office365.sharepoint.portal.home.datacachecollection import (
            SharePointHomeDataCacheCollection,
        )

        return self.properties.get("HomePageCache", SharePointHomeDataCacheCollection())

    @property
    def home_page_context(self) -> SharePointHomePageContext:
        """Gets the HomePageContext property"""
        from office365.sharepoint.portal.home.page_context import (
            SharePointHomePageContext,
        )

        return self.properties.get("HomePageContext", SharePointHomePageContext())

    @property
    def payload(self) -> Optional[str]:
        """Gets the Payload property"""
        return self.properties.get("Payload", None)

    @property
    def urls(self) -> StringCollection:
        """Gets the Urls property"""
        return self.properties.get("Urls", StringCollection())

    @property
    def dw_engine_token(self) -> TokenResponse:
        """Gets the DWEngineToken property"""
        from office365.sharepoint.oauth.token_response import TokenResponse

        return self.properties.get(
            "DWEngineToken", TokenResponse(self.context, ResourcePath("DWEngineToken", self.resource_path))
        )

    @property
    def token(self) -> TokenResponse:
        """Gets the Token property"""
        from office365.sharepoint.oauth.token_response import TokenResponse

        return self.properties.get("Token", TokenResponse(self.context, ResourcePath("Token", self.resource_path)))
