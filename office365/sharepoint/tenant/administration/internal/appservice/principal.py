from __future__ import annotations

from typing import Optional

from typing_extensions import Self

from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import GuidCollection, StringCollection
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.tenant.administration.internal.aad.collection import (
    SPO3rdPartyAADPermissionGrantCollection,
)
from office365.sharepoint.tenant.administration.internal.appservice.permission_grant import (
    SPOWebAppServicePrincipalPermissionGrant,
)
from office365.sharepoint.tenant.administration.internal.appservice.permission_request import (
    SPOWebAppServicePrincipalPermissionRequest,
)


class SPOWebAppServicePrincipal(Entity):
    def __init__(self, context):
        stat_path = ResourcePath("Microsoft.Online.SharePoint.TenantAdministration.Internal.SPOWebAppServicePrincipal")
        super().__init__(context, stat_path)

    def update_spfx_client_secret(self, secret_value: str):
        """Args:
        secret_value (str):
        """
        payload = {"secretValue": secret_value}
        qry = ServiceOperationQuery(self, "UpdateSpfxClientSecret", None, payload)
        self.context.add_query(qry)
        return self

    def update_spfx_third_party_app_id(self, app_id):
        payload = {"appId": app_id}
        qry = ServiceOperationQuery(self, "UpdateSpfxThirdPartyAppId", None, payload)
        self.context.add_query(qry)
        return self

    @property
    def account_enabled(self) -> Optional[bool]:
        """ """
        return self.properties.get("AccountEnabled", False)

    @property
    def app_id(self) -> Optional[bool]:
        """ """
        return self.properties.get("AppId", False)

    @property
    def reply_urls(self) -> StringCollection:
        """ """
        return self.properties.get("ReplyUrls", StringCollection())

    @property
    def grant_manager(self) -> SPO3rdPartyAADPermissionGrantCollection:
        return self.properties.get(
            "GrantManager",
            SPO3rdPartyAADPermissionGrantCollection(
                self.context,
                ResourcePath("GrantManager", self.resource_path),
            ),
        )

    @property
    def permission_grants(self) -> EntityCollection[SPOWebAppServicePrincipalPermissionGrant]:
        return self.properties.get(
            "PermissionGrants",
            EntityCollection(
                self.context,
                SPOWebAppServicePrincipalPermissionGrant,
                ResourcePath("PermissionGrants", self.resource_path),
            ),
        )

    @property
    def permission_requests(self) -> EntityCollection[SPOWebAppServicePrincipalPermissionRequest]:
        return self.properties.get(
            "PermissionRequests",
            EntityCollection(
                self.context,
                SPOWebAppServicePrincipalPermissionRequest,
                ResourcePath("PermissionRequests", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self):  # type: ignore[override]
        return "Microsoft.Online.SharePoint.TenantAdministration.Internal.SPOWebAppServicePrincipal"

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "GrantManager": self.grant_manager,
                "PermissionRequests": self.permission_requests,
                "PermissionGrants": self.permission_grants,
                "ReplyUrls": self.reply_urls,
            }
            default_value = property_mapping.get(name, None)
        return super().get_property(name, default_value)

    @property
    def app_helper_id(self) -> Optional[str]:
        """Gets the AppHelperId property"""
        return self.properties.get("AppHelperId", None)

    @property
    def apps_to_delete(self) -> StringCollection:
        """Gets the AppsToDelete property"""
        return self.properties.get("AppsToDelete", StringCollection())

    @property
    def service_principal_object_ids(self) -> GuidCollection:
        """Gets the ServicePrincipalObjectIds property"""
        return self.properties.get("ServicePrincipalObjectIds", GuidCollection())

    def remove_apps_to_delete(self, domains_to_delete: list[str]) -> Self:
        """RemoveAppsToDelete operation.

        Args:
            domains_to_delete (list[str]):
                domainsToDelete parameter
        """
        qry = ServiceOperationQuery(
            self, "RemoveAppsToDelete", None, {"domainsToDelete": StringCollection(domains_to_delete)}, None, None
        )
        self.context.add_query(qry)
        return self

    def update_spfx_third_party_isolated_component_fields(
        self, catalog_item_id: str, ap_app_object_id: str, sp_object_id: str, app_id: str
    ) -> Self:
        """UpdateSpfxThirdPartyIsolatedComponentFields operation.

        Args:
            catalog_item_id (str):
                catalogItemId parameter
            ap_app_object_id (str):
                apAppObjectId parameter
            sp_object_id (str):
                spObjectId parameter
            app_id (str):
                appId parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UpdateSpfxThirdPartyIsolatedComponentFields",
            None,
            {
                "catalogItemId": catalog_item_id,
                "apAppObjectId": ap_app_object_id,
                "spObjectId": sp_object_id,
                "appId": app_id,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def update_spfx_third_party_isolated_secret(self, service_principal_id: str, secret_value: str) -> Self:
        """UpdateSpfxThirdPartyIsolatedSecret operation.

        Args:
            service_principal_id (str):
                servicePrincipalId parameter
            secret_value (str):
                secretValue parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UpdateSpfxThirdPartyIsolatedSecret",
            None,
            {"servicePrincipalId": service_principal_id, "secretValue": secret_value},
            None,
            None,
        )
        self.context.add_query(qry)
        return self
