from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata
from office365.sharepoint.entity import Entity
from office365.sharepoint.viva.app_configuration import AppConfiguration
from office365.sharepoint.viva.connections.page import VivaConnectionsPage
from office365.sharepoint.viva.dashboard.configuration import DashboardConfiguration
from office365.sharepoint.viva.home import VivaHome

if TYPE_CHECKING:
    from office365.sharepoint.viva.configurationdata import ConfigurationData
    from office365.sharepoint.viva.connections.url_configuration import (
        VivaConnectionsUrlConfiguration,
    )
    from office365.sharepoint.viva.targetedsitedetails import TargetedSiteDetails
    from office365.sharepoint.viva.vivaresources import VivaResources


class EmployeeEngagement(Entity):
    """ """

    def __init__(self, context):
        super().__init__(context, ResourcePath("SP.EmployeeEngagement"))

    def dashboard_content(self, override_language_code: Optional[str] = None) -> ClientResult[str]:
        """Args:
        override_language_code (str):
        """
        return_type = ClientResult(self.context, str())
        payload = {"override_language_code": override_language_code}
        qry = ServiceOperationQuery(self, "DashboardContent", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def full_dashboard_content(
        self, canvas_as_json: Optional[bool] = None, include_personalization_data: Optional[bool] = None
    ) -> ClientResult[DashboardConfiguration]:
        """Args:
        canvas_as_json (bool):
        include_personalization_data (bool):
        """
        return_type = ClientResult(self.context, DashboardConfiguration())
        payload = {
            "canvasAsJson": canvas_as_json,
            "includePersonalizationData": include_personalization_data,
        }
        qry = ServiceOperationQuery(self, "FullDashboardContent", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def viva_home_configuration(self):
        return_type = ClientResult(self.context, {})
        qry = FunctionQuery(self, "VivaHomeConfiguration", None, return_type)
        self.context.add_query(qry)
        return return_type

    def viva_home(self) -> VivaHome:
        return_type = VivaHome(self.context)
        qry = ServiceOperationQuery(self, "VivaHome", return_type=return_type)
        self.context.add_query(qry)
        return return_type

    @odata(name="AppConfiguration")
    @property
    def app_configuration(self) -> AppConfiguration:
        return self.properties.get(
            "AppConfiguration",
            AppConfiguration(self.context, ResourcePath("AppConfiguration", self.resource_path)),
        )

    @odata(name="VivaConnectionsPage")
    @property
    def viva_connections_page(self) -> VivaConnectionsPage:
        return self.properties.get(
            "VivaConnectionsPage",
            VivaConnectionsPage(self.context, ResourcePath("VivaConnectionsPage", self.resource_path)),
        )

    @property
    def viva_resources(self) -> VivaResources:
        """Gets the VivaResources property"""
        from office365.sharepoint.viva.vivaresources import VivaResources

        return self.properties.get(
            "VivaResources", VivaResources(self.context, ResourcePath("VivaResources", self.resource_path))
        )

    def configuration(self) -> ClientResult[ConfigurationData]:
        """Configuration operation."""
        from office365.sharepoint.viva.configurationdata import ConfigurationData

        return_type = ClientResult(self.context, ConfigurationData())
        qry = FunctionQuery(self, "Configuration", [], return_type)
        self.context.add_query(qry)
        return return_type

    def configured_viva_connections_url(self) -> ClientResult[str]:
        """ConfiguredVivaConnectionsURL operation."""
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "ConfiguredVivaConnectionsURL", [], return_type)
        self.context.add_query(qry)
        return return_type

    def dashboard_oob_content(self, oob_content_choice: int) -> ClientResult[str]:
        """DashboardOOBContent operation.

        Args:
            oob_content_choice (int):
                oobContentChoice parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "DashboardOOBContent", [oob_content_choice], return_type)
        self.context.add_query(qry)
        return return_type

    def get_dashboard_personalization(self) -> ClientResult[bool]:
        """GetDashboardPersonalization operation."""
        return_type = ClientResult(self.context, bool())
        qry = FunctionQuery(self, "GetDashboardPersonalization", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_data_for_home(self) -> ClientResult[StringCollection]:
        """GetDataForHome operation."""
        return_type = ClientResult(self.context, StringCollection())
        qry = FunctionQuery(self, "GetDataForHome", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_targeted_sites_as_editor(self) -> ClientResult[ClientValueCollection[TargetedSiteDetails]]:
        """GetTargetedSitesAsEditor operation."""
        from office365.sharepoint.viva.targetedsitedetails import TargetedSiteDetails

        return_type = ClientResult(self.context, ClientValueCollection[TargetedSiteDetails]())
        qry = FunctionQuery(self, "GetTargetedSitesAsEditor", [], return_type)
        self.context.add_query(qry)
        return return_type

    def like_news_post(self, page_url: str, list_id: UUID, list_item_unique_id: UUID) -> Self:
        """LikeNewsPost operation.

        Args:
            page_url (str):
                pageUrl parameter
            list_id (UUID):
                listId parameter
            list_item_unique_id (UUID):
                listItemUniqueId parameter
        """
        qry = ServiceOperationQuery(
            self,
            "LikeNewsPost",
            None,
            {"pageUrl": page_url, "listId": list_id, "listItemUniqueId": list_item_unique_id},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_dashboard_personalization(self, is_enabled: bool) -> Self:
        """SetDashboardPersonalization operation.

        Args:
            is_enabled (bool):
                isEnabled parameter
        """
        qry = ServiceOperationQuery(self, "SetDashboardPersonalization", None, {"isEnabled": is_enabled}, None, None)
        self.context.add_query(qry)
        return self

    def unlike_news_post(self, page_url: str, list_id: UUID, list_item_unique_id: UUID) -> Self:
        """UnlikeNewsPost operation.

        Args:
            page_url (str):
                pageUrl parameter
            list_id (UUID):
                listId parameter
            list_item_unique_id (UUID):
                listItemUniqueId parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UnlikeNewsPost",
            None,
            {"pageUrl": page_url, "listId": list_id, "listItemUniqueId": list_item_unique_id},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def viva_connections(self, admin_configured_url: str) -> ClientResult[VivaConnectionsUrlConfiguration]:
        """VivaConnections operation.

        Args:
            admin_configured_url (str):
                adminConfiguredUrl parameter
        """
        from office365.sharepoint.viva.connections.url_configuration import (
            VivaConnectionsUrlConfiguration,
        )

        return_type = ClientResult(self.context, VivaConnectionsUrlConfiguration())
        qry = ServiceOperationQuery(
            self, "VivaConnections", None, {"adminConfiguredUrl": admin_configured_url}, None, return_type
        )
        self.context.add_query(qry)
        return return_type
