from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.directory.applications.permissiontype import PermissionType


class PermissionGrantConditionSet(Entity):
    """
    A permission grant condition set is used to specify a matching rule in a permission grant policy to include
    or exclude a permission grant event.

    A permission grant condition set contains several conditions. For an event to match a permission grant condition
    set, all conditions must be met.
    """

    @property
    def client_application_ids(self) -> StringCollection:
        """
        A list of appId values for the client applications to match with, or a list with the single value all to
        match any client application. Default is the single value all.
        """
        return self.properties.get("clientApplicationIds", StringCollection())

    @property
    def client_application_publisher_ids(self) -> StringCollection:
        """
        A list of Microsoft Partner Network (MPN) IDs for verified publishers of the client application,  or a list
        with the single value all to match with client apps from any publisher. Default is the single value all.
        """
        return self.properties.get("clientApplicationPublisherIds", StringCollection())

    @property
    def client_applications_from_verified_publisher_only(self) -> Optional[bool]:
        """
        Set to true to only match on client applications with a verified publisher. Set to false to match on any client
        app, even if it does not have a verified publisher. Default is false.
        """
        return self.properties.get("clientApplicationsFromVerifiedPublisherOnly", None)

    @property
    def permissions(self) -> StringCollection:
        """
        The list of id values for the specific permissions to match with, or a list with the single value all to
        match with any permission. The id of delegated permissions can be found in the oauth2PermissionScopes property
        of the API's servicePrincipal object. The id of application permissions can be found in the appRoles property
        of the API's servicePrincipal object. The id of resource-specific application permissions can be found in
        the resourceSpecificApplicationPermissions property of the API's servicePrincipal object.
        Default is the single value all.
        """
        return self.properties.get("permissions", StringCollection())

    @property
    def resource_application(self) -> Optional[str]:
        """
        The appId of the resource application (e.g. the API) for which a permission is being granted, or any to match
        with any resource application or API. Default is any.
        """
        return self.properties.get("resourceApplication", None)

    @property
    def client_application_tenant_ids(self) -> StringCollection:
        """Gets the clientApplicationTenantIds property"""
        return self.properties.get("clientApplicationTenantIds", StringCollection())

    @property
    def permission_classification(self) -> Optional[str]:
        """Gets the permissionClassification property"""
        return self.properties.get("permissionClassification", None)

    @property
    def permission_type(self) -> PermissionType:
        """Gets the permissionType property"""
        from office365.directory.applications.permissiontype import PermissionType

        return self.properties.get("permissionType", PermissionType.application)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PermissionGrantConditionSet"
