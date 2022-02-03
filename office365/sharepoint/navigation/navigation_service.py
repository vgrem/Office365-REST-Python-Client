from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.navigation.menu_state import MenuState


class NavigationService(BaseEntity):

    def __init__(self, context):
        """The entry point for REST-based navigation service operations."""
        super(NavigationService, self).__init__(context,
                                                ResourcePath("Microsoft.SharePoint.Navigation.REST.NavigationServiceRest"))

    def get_publishing_navigation_provider_type(self, mapProviderName="SPNavigationProvider"):
        """
        Gets a publishing navigation provider type when publishing feature is turned on for the site (2).
        If navigation provider is not found on the site MUST return InvalidSiteMapProvider type.

        :param str mapProviderName: The server will use "SPNavigationProvider" as provider name
            if mapProviderName is not specified.
        :return:
        """
        result = ClientResult(self.context)
        params = {"mapProviderName": mapProviderName}
        qry = ServiceOperationQuery(self, "GetPublishingNavigationProviderType", params, None, None, result)
        self.context.add_query(qry)
        return result

    def global_nav(self):
        return_type = MenuState()
        qry = ServiceOperationQuery(self, "GlobalNav", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def global_nav_enabled(self):
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "GlobalNavEnabled", None, None, None, result)
        self.context.add_query(qry)
        return result

    def set_global_nav_enabled(self, is_enabled):
        """
        :param bool is_enabled:
        :return:
        """
        qry = ServiceOperationQuery(self, "SetGlobalNavEnabled", None, {"isEnabled": is_enabled}, None)
        self.context.add_query(qry)
        return self

    def menu_node_key(self, currentUrl):
        pass

    def save_menu_state(self):
        pass
