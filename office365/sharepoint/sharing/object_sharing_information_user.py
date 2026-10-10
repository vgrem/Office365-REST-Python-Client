from __future__ import annotations

from typing import Optional

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity
from office365.sharepoint.principal.principal import Principal
from office365.sharepoint.principal.users.user import User


class ObjectSharingInformationUser(Entity):
    """Contains information about a principal with whom a securable object is shared. It can be a user or a group."""

    @property
    def email(self) -> Optional[str]:
        """Specifies the email address for the user."""
        return self.properties.get("Email", None)

    @property
    def sip_address(self) -> Optional[str]:
        """Specifies the SIP address of the user."""
        return self.properties.get("SipAddress", None)

    @property
    def login_name(self) -> Optional[str]:
        """Specifies the login name for the principal."""
        return self.properties.get("LoginName", None)

    def principal(self):
        """The principal with whom a securable object is shared. It is either a user or a group."""
        return self.properties.get(
            "Principal",
            Principal(self.context, ResourcePath("Principal", self.resource_path)),
        )

    def user(self):
        """Specifies the user with whom a securable object is shared."""
        return self.properties.get("User", User(self.context, ResourcePath("User", self.resource_path)))

    @property
    def custom_role_names(self) -> Optional[str]:
        """Gets the CustomRoleNames property"""
        return self.properties.get("CustomRoleNames", None)

    @property
    def department(self) -> Optional[str]:
        """Gets the Department property"""
        return self.properties.get("Department", None)

    @property
    def has_edit_permission(self) -> Optional[bool]:
        """Gets the HasEditPermission property"""
        return self.properties.get("HasEditPermission", None)

    @property
    def has_review_permission(self) -> Optional[bool]:
        """Gets the HasReviewPermission property"""
        return self.properties.get("HasReviewPermission", None)

    @property
    def has_view_permission(self) -> Optional[bool]:
        """Gets the HasViewPermission property"""
        return self.properties.get("HasViewPermission", None)

    @property
    def id(self) -> Optional[int]:
        """Gets the Id property"""
        return self.properties.get("Id", None)

    @property
    def is_domain_group(self) -> Optional[bool]:
        """Gets the IsDomainGroup property"""
        return self.properties.get("IsDomainGroup", None)

    @property
    def is_external_user(self) -> Optional[bool]:
        """Gets the IsExternalUser property"""
        return self.properties.get("IsExternalUser", None)

    @property
    def is_member_of_group(self) -> Optional[bool]:
        """Gets the IsMemberOfGroup property"""
        return self.properties.get("IsMemberOfGroup", None)

    @property
    def is_site_admin(self) -> Optional[bool]:
        """Gets the IsSiteAdmin property"""
        return self.properties.get("IsSiteAdmin", None)

    @property
    def job_title(self) -> Optional[str]:
        """Gets the JobTitle property"""
        return self.properties.get("JobTitle", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the Name property"""
        return self.properties.get("Name", None)

    @property
    def picture(self) -> Optional[str]:
        """Gets the Picture property"""
        return self.properties.get("Picture", None)
