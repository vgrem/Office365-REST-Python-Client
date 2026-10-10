from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.sites.site import Site
from office365.sharepoint.userprofiles.followed_content import FollowedContent


class UserProfile(Entity):
    """The UserProfile class stores the profile of the individual user, which includes properties such
    as the user's account name, preferred name, and email address."""

    def __str__(self):
        return self.display_name or self.entity_type_name

    def __repr__(self):
        return self.account_name or self.entity_type_name

    @property
    def account_name(self) -> Optional[str]:
        """The account name of the user."""
        return self.properties.get("AccountName", None)

    @property
    def display_name(self) -> Optional[str]:
        """The title of the user."""
        return self.properties.get("DisplayName", None)

    @property
    def follow_personal_site_url(self) -> Optional[str]:
        """The FollowPersonalSiteUrl property specifies the URL to allow the current user to create a personal site.
        If there is no hybrid & cross-geo setting, it will return the same value as UrlToCreatePersonalSite,
        otherwise a URL to allow the current user to create a personal site on the remote host.
        """
        return self.properties.get("FollowPersonalSiteUrl", None)

    @property
    def is_default_document_library_blocked(self) -> Optional[bool]:
        """If true, indicates that the access of the user to the default document library in the user’s OneDrive
        is blocked."""
        return self.properties.get("IsDefaultDocumentLibraryBlocked", None)

    @property
    def is_people_list_public(self) -> Optional[bool]:
        """Specifies whether the list of people that the user is following is public."""
        return self.properties.get("IsPeopleListPublic", None)

    @property
    def is_privacy_setting_on(self) -> Optional[bool]:
        """Specifies whether the privacy setting has been set for the site."""
        return self.properties.get("IsPrivacySettingOn", None)

    @property
    def is_self(self) -> Optional[bool]:
        """Specifies whether the user profile is for the current user."""
        return self.properties.get("IsSelf", None)

    @property
    def job_title(self) -> Optional[str]:
        """Specifies the job title of the user."""
        return self.properties.get("JobTitle", None)

    @property
    def my_site_first_run_experience(self) -> Optional[int]:
        """Specifies the personal site First Run flag of the user."""
        return self.properties.get("MySiteFirstRunExperience", None)

    @property
    def my_site_host_url(self) -> Optional[str]:
        """Specifies the URL for the personal site of the current user."""
        return self.properties.get("MySiteHostUrl", None)

    @property
    def o15_first_run_experience(self) -> Optional[int]:
        """Specifies the First Run flag of the user."""
        return self.properties.get("O15FirstRunExperience", None)

    @property
    def personal_site_capabilities(self) -> Optional[int]:
        """The PersonalSiteCapabilities property specifies attributes of the user's personal site."""
        return self.properties.get("PersonalSiteCapabilities", None)

    @property
    def personal_site_first_creation_error(self) -> Optional[str]:
        """Specifies the failure for the personal site first creation attempt."""
        return self.properties.get("PersonalSiteFirstCreationError", None)

    @property
    def personal_site_first_creation_time(self) -> Optional[datetime]:
        """Specifies the time for the personal site first creation attempt."""
        return self.properties.get("PersonalSiteFirstCreationTime", datetime.min)

    @property
    def picture_url(self) -> Optional[str]:
        """Specifies the photo URL for the current user."""
        return self.properties.get("PictureUrl", None)

    @property
    def public_url(self) -> Optional[str]:
        """Specifies the public URL for the personal site of the current user."""
        return self.properties.get("PublicUrl", None)

    @property
    def url_to_create_personal_site(self) -> Optional[str]:
        """
        The UrlToCreatePersonalSite property specifies the URL to allow the current user to create a personal site.
        """
        return self.properties.get("UrlToCreatePersonalSite", None)

    @property
    def followed_content(self) -> FollowedContent:
        """Gets a FollowedContent object for the user."""
        return self.properties.get(
            "FollowedContent",
            FollowedContent(self.context, ResourcePath("FollowedContent", self.resource_path)),
        )

    @property
    def personal_site(self) -> Site:
        """The PersonalSite property specifies the user's personal site"""
        return self.properties.get(
            "PersonalSite",
            Site(self.context, ResourcePath("PersonalSite", self.resource_path)),
        )

    def create_personal_site(self, lcid):
        """The CreatePersonalSite method creates a personal site (2) for this user, which can be used to share documents,
        web pages, and other files.

        Args:
            lcid (int): Specifies the locale identifier for the site.
        """
        payload = {"lcid": lcid}
        qry = ServiceOperationQuery(self, "CreatePersonalSite", None, payload)
        self.context.add_query(qry)
        return self

    def create_personal_site_enque(self, is_interactive):
        """Enqueues creating a personal site for this user, which can be used to share documents, web pages,
        and other files.

        Args:
            is_interactive (bool): Has a true value if the request is from a web browser and a false value if the
                request is from a client application.
        """
        payload = {"isInteractive": is_interactive}
        qry = ServiceOperationQuery(self, "CreatePersonalSiteEnque", None, payload)
        self.context.add_query(qry)
        return self

    def set_my_site_first_run_experience(self, value):
        """Sets the personal site First Run flag for the user.

        Args:
            value (str): The value to be set for the First Run flag.
        """
        payload = {"value": value}
        qry = ServiceOperationQuery(self, "SetMySiteFirstRunExperience", None, payload)
        self.context.add_query(qry)
        return self

    def share_all_social_data(self, share_all):
        """The ShareAllSocialData method specifies whether the current user's social data is to be shared.

        Args:
            share_all (bool): If true, social data is shared; if false, social data is not shared.
        """
        payload = {"shareAll": share_all}
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "ShareAllSocialData", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "FollowedContent": self.followed_content,
                "PersonalSite": self.personal_site,
                "PersonalSiteFirstCreationTime": self.personal_site_first_creation_time,
            }
            default_value = property_mapping.get(name, None)
        return super().get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super().set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "AccountName":
            pass
        return self

    @property
    def entity_type_name(self):
        return "SP.UserProfiles.UserProfile"

    @property
    def personal_site_instantiation_state(self) -> Optional[int]:
        """Gets the PersonalSiteInstantiationState property"""
        return self.properties.get("PersonalSiteInstantiationState", None)

    @property
    def personal_site_last_creation_time(self) -> Optional[datetime]:
        """Gets the PersonalSiteLastCreationTime property"""
        return self.properties.get("PersonalSiteLastCreationTime", datetime.min)

    @property
    def personal_site_number_of_retries(self) -> Optional[int]:
        """Gets the PersonalSiteNumberOfRetries property"""
        return self.properties.get("PersonalSiteNumberOfRetries", None)

    @property
    def picture_import_enabled(self) -> Optional[bool]:
        """Gets the PictureImportEnabled property"""
        return self.properties.get("PictureImportEnabled", None)

    @property
    def sip_address(self) -> Optional[str]:
        """Gets the SipAddress property"""
        return self.properties.get("SipAddress", None)

    def create_personal_site_from_work_item(self, work_item_type: UUID) -> ClientResult[int]:
        """CreatePersonalSiteFromWorkItem operation.

        Args:
            work_item_type (UUID):
                workItemType parameter
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(
            self, "CreatePersonalSiteFromWorkItem", None, {"workItemType": work_item_type}, None, return_type
        )
        self.context.add_query(qry)
        return return_type
