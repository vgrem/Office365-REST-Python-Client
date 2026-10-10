from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.apps.properties import AppProperties
    from office365.sharepoint.client_context import ClientContext


class AppTileProperties(Entity):
    @staticmethod
    def get_app_properties(
        context: ClientContext,
        app_id: UUID,
        app_type: int,
        product_id: UUID,
        app_source: int,
        asset_id: str,
        content_market: str,
        is_tenant_app: bool,
    ) -> ClientResult[AppProperties]:
        """GetAppProperties operation.

        Args:
            app_id (UUID):
                appId parameter
            app_type (int):
                appType parameter
            product_id (UUID):
                productId parameter
            app_source (int):
                appSource parameter
            asset_id (str):
                assetId parameter
            content_market (str):
                contentMarket parameter
            is_tenant_app (bool):
                isTenantApp parameter
        """
        from office365.sharepoint.apps.apptileproperties import AppTileProperties
        from office365.sharepoint.apps.properties import AppProperties

        return_type = ClientResult(context, AppProperties())
        qry = ServiceOperationQuery(
            AppTileProperties(context),
            "GetAppProperties",
            None,
            {
                "appId": app_id,
                "appType": app_type,
                "productId": product_id,
                "appSource": app_source,
                "assetId": asset_id,
                "contentMarket": content_market,
                "isTenantApp": is_tenant_app,
            },
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type
