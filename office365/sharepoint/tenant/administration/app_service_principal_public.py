from __future__ import annotations

from typing_extensions import Self

from office365.runtime.paths.v3.static import StaticPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity


class SPOWebAppServicePrincipalPublic(Entity):
    """ """

    def __init__(self, context):
        """ """
        static_path = StaticPath("Microsoft.Online.SharePoint.TenantAdministration.SPOWebAppServicePrincipalPublic")
        super().__init__(context, static_path)

    @property
    def entity_type_name(self):  # type: ignore[override]
        return "Microsoft.Online.SharePoint.TenantAdministration.SPOWebAppServicePrincipalPublic"

    def add_custom_spfx3rd_party_app_principal(self, app_id: str, app_uri: str, client_secret: str) -> Self:
        """AddCustomSpfx3rdPartyAppPrincipal operation.

        Args:
            app_id (str):
                appId parameter
            app_uri (str):
                appUri parameter
            client_secret (str):
                clientSecret parameter
        """
        qry = ServiceOperationQuery(
            self,
            "AddCustomSpfx3rdPartyAppPrincipal",
            None,
            {"appId": app_id, "appUri": app_uri, "clientSecret": client_secret},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def remove_custom_spfx3rd_party_app_principal(self) -> Self:
        """RemoveCustomSpfx3rdPartyAppPrincipal operation."""
        qry = ServiceOperationQuery(self, "RemoveCustomSpfx3rdPartyAppPrincipal", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def update_custom_spfx3rd_party_app_principal_client_secret(self, client_secret: str) -> Self:
        """UpdateCustomSpfx3rdPartyAppPrincipalClientSecret operation.

        Args:
            client_secret (str):
                clientSecret parameter
        """
        qry = ServiceOperationQuery(
            self, "UpdateCustomSpfx3rdPartyAppPrincipalClientSecret", None, {"clientSecret": client_secret}, None, None
        )
        self.context.add_query(qry)
        return self
