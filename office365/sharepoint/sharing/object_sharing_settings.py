from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sharing.object_sharing_information import ObjectSharingInformation
from office365.sharepoint.sharing.sharepoint_sharing_settings import SharePointSharingSettings
from office365.sharepoint.sharing.permission_information import SharingPermissionInformation


class ObjectSharingSettings(BaseEntity):
    """This class contains the information necessary to read and change the sharing status of a SharePoint object.
    It also contains a reference to SharePoint specific settings denoted by "SharePointSettings".
    """

    @property
    def web_url(self):
        """
        The URL pointing to the containing SP.Web object.

        :rtype: str
        """
        return self.properties.get("WebUrl", None)

    @property
    def access_request_mode(self):
        """
        Boolean indicating whether the sharing context operates under the access request mode.

        :rtype: bool
        """
        return self.properties.get("AccessRequestMode", None)

    @property
    def can_send_email(self):
        """
        Boolean indicating whether email invitations can be sent.

        :return: bool
        """
        return self.properties.get("CanSendEmail", None)

    @property
    def is_user_site_admin(self):
        """
        Boolean that indicates whether or not the current user is a site collection administrator.

        :return: bool
        """
        return self.properties.get("IsUserSiteAdmin", None)

    @property
    def roles(self):
        """
        A dictionary object that lists the display name and the id of the SharePoint regular roles.
        """
        return self.properties.get("Roles", None)

    @property
    def object_sharing_information(self):
        """
        Contains information about the sharing state of a shareable object.
        """
        return self.properties.get("ObjectSharingInformation",
                                   ObjectSharingInformation(self.context,
                                                            ResourcePath("ObjectSharingInformation",
                                                                         self.resource_path)))

    @property
    def sharepoint_settings(self):
        """
        An object that contains the SharePoint UI specific sharing settings.
        """
        return self.properties.get("SharePointSettings",
                                   SharePointSharingSettings(self.context,
                                                             ResourcePath("SharePointSettings", self.resource_path)))

    @property
    def sharing_permissions(self):
        """
        A list of SharingPermissionInformation objects that can be used to share.
        """
        return self.properties.get("SharingPermissions",
                                   SharingPermissionInformation(self.context,
                                                                ResourcePath("SharingPermissions", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "ObjectSharingInformation": self.object_sharing_information,
                "SharePointSettings": self.sharepoint_settings,
                "SharingPermissions": self.sharing_permissions
            }
            default_value = property_mapping.get(name, None)
        return super(ObjectSharingSettings, self).get_property(name, default_value)
