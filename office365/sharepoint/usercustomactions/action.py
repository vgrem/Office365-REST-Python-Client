from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.permissions.base_permissions import BasePermissions
    from office365.sharepoint.translation.user_resource import UserResource


class UserCustomAction(Entity):
    """Represents a custom action associated with a SharePoint list, Web site, or subsite."""

    @property
    def client_side_component_id(self) -> Optional[str]:
        """"""
        return self.properties.get("ClientSideComponentId", None)

    @property
    def script_block(self) -> Optional[str]:
        """Gets the value that specifies the ECMAScript to be executed when the custom action is performed."""
        return self.properties.get("ScriptBlock", None)

    @script_block.setter
    def script_block(self, value: str) -> None:
        """
        Sets the value that specifies the ECMAScript to be executed when the custom action is performed.
        """
        self.set_property("ScriptBlock", value)

    @property
    def script_src(self) -> Optional[str]:
        """Gets a value that specifies the URI of a file which contains the ECMAScript to execute on the page"""
        return self.properties.get("ScriptSrc", None)

    @script_src.setter
    def script_src(self, value: str) -> None:
        """
        Sets a value that specifies the URI of a file which contains the ECMAScript to execute on the page
        """
        self.set_property("ScriptSrc", value)

    @property
    def url(self) -> Optional[str]:
        """Gets or sets the URL, URI, or ECMAScript (JScript, JavaScript) function associated with the action."""
        return self.properties.get("Url", None)

    @property
    def client_side_component_properties(self) -> Optional[str]:
        """Gets the ClientSideComponentProperties property"""
        return self.properties.get("ClientSideComponentProperties", None)

    @property
    def command_ui_extension(self) -> Optional[str]:
        """Gets the CommandUIExtension property"""
        return self.properties.get("CommandUIExtension", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)

    @property
    def group(self) -> Optional[str]:
        """Gets the Group property"""
        return self.properties.get("Group", None)

    @property
    def host_properties(self) -> Optional[str]:
        """Gets the HostProperties property"""
        return self.properties.get("HostProperties", None)

    @property
    def id(self) -> Optional[UUID]:
        """Gets the Id property"""
        return self.properties.get("Id", None)

    @property
    def image_url(self) -> Optional[str]:
        """Gets the ImageUrl property"""
        return self.properties.get("ImageUrl", None)

    @property
    def location(self) -> Optional[str]:
        """Gets the Location property"""
        return self.properties.get("Location", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the Name property"""
        return self.properties.get("Name", None)

    @property
    def registration_id(self) -> Optional[str]:
        """Gets the RegistrationId property"""
        return self.properties.get("RegistrationId", None)

    @property
    def registration_type(self) -> Optional[int]:
        """Gets the RegistrationType property"""
        return self.properties.get("RegistrationType", None)

    @property
    def rights(self) -> BasePermissions:
        """Gets the Rights property"""
        from office365.sharepoint.permissions.base_permissions import BasePermissions

        return self.properties.get("Rights", BasePermissions())

    @property
    def scope(self) -> Optional[int]:
        """Gets the Scope property"""
        return self.properties.get("Scope", None)

    @property
    def sequence(self) -> Optional[int]:
        """Gets the Sequence property"""
        return self.properties.get("Sequence", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def version_of_user_custom_action(self) -> Optional[str]:
        """Gets the VersionOfUserCustomAction property"""
        return self.properties.get("VersionOfUserCustomAction", None)

    @property
    def description_resource(self) -> UserResource:
        """Gets the DescriptionResource property"""
        from office365.sharepoint.translation.user_resource import UserResource

        return self.properties.get(
            "DescriptionResource", UserResource(self.context, ResourcePath("DescriptionResource", self.resource_path))
        )

    @property
    def title_resource(self) -> UserResource:
        """Gets the TitleResource property"""
        from office365.sharepoint.translation.user_resource import UserResource

        return self.properties.get(
            "TitleResource", UserResource(self.context, ResourcePath("TitleResource", self.resource_path))
        )
