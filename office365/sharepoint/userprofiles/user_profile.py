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

    def create_personal_site_enque(self, is_interactive):
        """
        Enqueues creating a personal site for this user, which can be used to share documents, web pages,
            and other files.

        :type is_interactive: bool
        """
        payload = {"isInteractive": is_interactive}
        qry = ServiceOperationQuery(self, "CreatePersonalSiteEnque", None, payload, None, None)
        self.context.add_query(qry)
        return self

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
