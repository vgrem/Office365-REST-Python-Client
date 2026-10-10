from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class AppInstance(Entity):
    @property
    def app_principal_id(self) -> Optional[str]:
        """Gets the AppPrincipalId property"""
        return self.properties.get("AppPrincipalId", None)

    @property
    def app_web_full_url(self) -> Optional[str]:
        """Gets the AppWebFullUrl property"""
        return self.properties.get("AppWebFullUrl", None)

    @property
    def image_fallback_url(self) -> Optional[str]:
        """Gets the ImageFallbackUrl property"""
        return self.properties.get("ImageFallbackUrl", None)

    @property
    def image_url(self) -> Optional[str]:
        """Gets the ImageUrl property"""
        return self.properties.get("ImageUrl", None)

    @property
    def in_error(self) -> Optional[bool]:
        """Gets the InError property"""
        return self.properties.get("InError", None)

    @property
    def start_page(self) -> Optional[str]:
        """Gets the StartPage property"""
        return self.properties.get("StartPage", None)

    @property
    def package_fingerprint(self) -> Optional[bytes]:
        """Gets the PackageFingerprint property"""
        return self.properties.get("PackageFingerprint", None)

    @property
    def product_id(self) -> Optional[UUID]:
        """Gets the ProductId property"""
        return self.properties.get("ProductId", None)

    @property
    def remote_app_url(self) -> Optional[str]:
        """Gets the RemoteAppUrl property"""
        return self.properties.get("RemoteAppUrl", None)

    @property
    def settings_page_url(self) -> Optional[str]:
        """Gets the SettingsPageUrl property"""
        return self.properties.get("SettingsPageUrl", None)

    @property
    def site_id(self) -> Optional[UUID]:
        """Gets the SiteId property"""
        return self.properties.get("SiteId", None)

    @property
    def status(self) -> Optional[int]:
        """Gets the Status property"""
        return self.properties.get("Status", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def web_id(self) -> Optional[UUID]:
        """Gets the WebId property"""
        return self.properties.get("WebId", None)

    @property
    def id(self) -> Optional[UUID]:
        """Gets the Id property"""
        return self.properties.get("Id", None)

    def cancel_all_jobs(self) -> ClientResult[bool]:
        """CancelAllJobs operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "CancelAllJobs", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_app_database_connection_string(self) -> ClientResult[str]:
        """GetAppDatabaseConnectionString operation."""
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetAppDatabaseConnectionString", [], return_type)
        self.context.add_query(qry)
        return return_type

    def install(self) -> ClientResult[UUID]:
        """Install operation."""
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(self, "Install", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def recycle(self) -> ClientResult[UUID]:
        """Recycle operation."""
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(self, "Recycle", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def restore(self) -> ClientResult[UUID]:
        """Restore operation."""
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(self, "Restore", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def retrieve_app_database_connection_string(context: ClientContext) -> ClientResult[str]:
        """RetrieveAppDatabaseConnectionString operation."""
        from office365.sharepoint.apps.instance import AppInstance

        return_type = ClientResult(context, str())
        qry = ServiceOperationQuery(
            AppInstance(context), "RetrieveAppDatabaseConnectionString", None, {}, None, return_type, True
        )
        context.add_query(qry)
        return return_type

    def retry_all_jobs(self) -> Self:
        """RetryAllJobs operation."""
        qry = ServiceOperationQuery(self, "RetryAllJobs", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def uninstall(self) -> ClientResult[UUID]:
        """Uninstall operation."""
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(self, "Uninstall", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def upgrade(self, app_package_stream: bytes) -> Self:
        """Upgrade operation.

        Args:
            app_package_stream (bytes):
                appPackageStream parameter
        """
        qry = ServiceOperationQuery(self, "Upgrade", None, {"appPackageStream": app_package_stream}, None, None)
        self.context.add_query(qry)
        return self
