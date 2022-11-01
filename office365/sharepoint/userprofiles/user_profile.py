from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sites.site import Site
from office365.sharepoint.userprofiles.followed_content import FollowedContent


class UserProfile(BaseEntity):
    """The UserProfile class stores the profile of the individual user, which includes properties such
    as the user's account name, preferred name, and email address."""

    @property
    def account_name(self):
        """
        The account name of the user.

        :rtype: str or None
        """
        return self.properties.get("AccountName", None)

    @property
    def display_name(self):
        """
        The title of the user.

        :rtype: str or None
        """
        return self.properties.get("DisplayName", None)

    @property
    def my_site_host_url(self):
        """
        Specifies the URL for the personal site of the current user.

        :rtype: str or None
        """
        return self.properties.get("MySiteHostUrl", None)

    @property
    def public_url(self):
        """
        Specifies the public URL for the personal site of the current user.

        :rtype: str or None
        """
        return self.properties.get("PublicUrl", None)

    @property
    def url_to_create_personal_site(self):
        """
        The UrlToCreatePersonalSite property specifies the URL to allow the current user to create a personal site.

        :rtype: str or None
        """
        return self.properties.get("UrlToCreatePersonalSite", None)

    @property
    def followed_content(self):
        """
        Gets a FollowedContent object for the user.
        """
        return self.properties.get("FollowedContent",
                                   FollowedContent(self.context, ResourcePath("FollowedContent", self.resource_path)))

    @property
    def personal_site(self):
        """
        The PersonalSite property specifies the user's personal site
        """
        return self.properties.get("PersonalSite",
                                   Site(self.context, ResourcePath("PersonalSite", self.resource_path)))

    def create_personal_site(self, lcid):
        """
        The CreatePersonalSite method creates a personal site (2) for this user, which can be used to share documents,
        web pages, and other files.

        :param int lcid: Specifies the locale identifier for the site.
        """
        payload = {"lcid": lcid}
        qry = ServiceOperationQuery(self, "CreatePersonalSite", None, payload)
        self.context.add_query(qry)
        return self

    def create_personal_site_enque(self, is_interactive):
        """
        Enqueues creating a personal site for this user, which can be used to share documents, web pages,
            and other files.

        :type is_interactive: bool
        """
        payload = {"isInteractive": is_interactive}
        qry = ServiceOperationQuery(self, "CreatePersonalSiteEnque", None, payload)
        self.context.add_query(qry)
        return self

    def set_my_site_first_run_experience(self, value):
        """
        Sets the personal site First Run flag for the user.

        :param str value: The value to be set for the First Run flag.
        """
        payload = {"value": value}
        qry = ServiceOperationQuery(self, "SetMySiteFirstRunExperience", None, payload)
        self.context.add_query(qry)
        return self

    def share_all_social_data(self, share_all):
        """
        The ShareAllSocialData method specifies whether the current user's social data is to be shared.

        :param bool share_all:  If true, social data is shared; if false, social data is not shared.
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
                "PersonalSite": self.personal_site
            }
            default_value = property_mapping.get(name, None)
        return super(UserProfile, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(UserProfile, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "AccountName":
            pass
        return self

    @property
    def entity_type_name(self):
        return "SP.UserProfiles.UserProfile"
