from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.navigation.menu_state import MenuState


class NavigationService(BaseEntity):
    """The entry point for REST-based navigation service operations."""

    def __init__(self, context):
        """The entry point for REST-based navigation service operations."""
        service_path = ResourcePath("Microsoft.SharePoint.Navigation.REST.NavigationServiceRest")
        super(NavigationService, self).__init__(context, service_path)

    def get_publishing_navigation_provider_type(self, map_provider_name="SPNavigationProvider"):
        """
        Gets a publishing navigation provider type when publishing feature is turned on for the site (2).
        If navigation provider is not found on the site MUST return InvalidSiteMapProvider type.

        :param str map_provider_name: The server will use "SPNavigationProvider" as provider name
            if mapProviderName is not specified.
        :return:
        """
        return_type = ClientResult(self.context)
        params = {"mapProviderName": map_provider_name}
        qry = ServiceOperationQuery(self, "GetPublishingNavigationProviderType", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

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

    def menu_node_key(self, current_url, map_provider_name=None):
        """
        Returns the unique key for a node within the menu tree. If a key cannot be found, an exception is returned.

        :param str current_url: A URL relative to the site collection identifying the node within the menu tree.
        :param str map_provider_name: The name identifying a provider to use for the lookup
        """
        return_type = ClientResult(self.context)
        params = {
            "currentUrl": current_url,
            "mapProviderName": map_provider_name
        }
        qry = ServiceOperationQuery(self, "MenuNodeKey", None, params, None, return_type)
        self.context.add_query(qry)
        return return_type

    def save_menu_state(self):
        """Updates the menu tree rooted at the specified root node for a given provider."""
        pass

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Navigation.REST.NavigationServiceRest"
