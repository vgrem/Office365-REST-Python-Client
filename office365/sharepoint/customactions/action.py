from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity
from office365.sharepoint.permissions.base_permissions import BasePermissions
from office365.sharepoint.translation.user_resource import UserResource


class UserCustomAction(Entity):
    """Specifies a custom action."""

    def get_property(self, name, default_value=None):
        if name == "DescriptionResource":
            default_value = self.description_resource
        elif name == "TitleResource":
            default_value = self.title_resource
        return super().get_property(name, default_value)

    @property
    def rights(self) -> BasePermissions:
        """Specifies the permissions needed for the custom action."""
        return self.properties.get("Rights", BasePermissions())

    @property
    def description_resource(self) -> UserResource:
        """Gets the SP.UserResource object that corresponds to the Description for this object."""
        return self.properties.get(
            "DescriptionResource",
            UserResource(self.context, ResourcePath("DescriptionResource", self.resource_path)),
        )

    @property
    def title_resource(self) -> UserResource:
        """Returns the UserResource object that corresponds to the Title for this object."""
        return self.properties.get(
            "TitleResource",
            UserResource(self.context, ResourcePath("TitleResource", self.resource_path)),
        )

    @property
    def client_side_component_id(self) -> Optional[UUID]:
        """Gets the ClientSideComponentId property"""
        return self.properties.get("ClientSideComponentId", None)

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
    def scope(self) -> Optional[int]:
        """Gets the Scope property"""
        return self.properties.get("Scope", None)

    @property
    def script_block(self) -> Optional[str]:
        """Gets the ScriptBlock property"""
        return self.properties.get("ScriptBlock", None)

    @property
    def script_src(self) -> Optional[str]:
        """Gets the ScriptSrc property"""
        return self.properties.get("ScriptSrc", None)

    @property
    def sequence(self) -> Optional[int]:
        """Gets the Sequence property"""
        return self.properties.get("Sequence", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def url(self) -> Optional[str]:
        """Gets the Url property"""
        return self.properties.get("Url", None)

    @property
    def version_of_user_custom_action(self) -> Optional[str]:
        """Gets the VersionOfUserCustomAction property"""
        return self.properties.get("VersionOfUserCustomAction", None)
