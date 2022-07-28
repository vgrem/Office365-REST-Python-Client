from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.alerts.collection import AlertCollection
from office365.sharepoint.principal.principal import Principal
from office365.sharepoint.principal.user_id_info import UserIdInfo


class User(Principal):
    """Represents a user in Microsoft SharePoint Foundation. A user is a type of SP.Principal."""

    def get_personal_site(self):
        """Get personal site"""
        from office365.sharepoint.sites.site import Site
        site = Site(self.context)

        def _user_loaded():
            from office365.sharepoint.userprofiles.people_manager import PeopleManager
            people_manager = PeopleManager(self.context)
            person_props = people_manager.get_properties_for(self.login_name)

            def _person_props_loaded(resp):
                site.set_property("__siteUrl", person_props.personal_url)
            self.context.after_execute(_person_props_loaded)

        self.ensure_property("LoginName", _user_loaded)
        return site

    @property
    def groups(self):
        """Gets a collection of group objects that represents all of the groups for the user."""
        from office365.sharepoint.principal.group_collection import GroupCollection
        return self.properties.get('Groups',
                                   GroupCollection(self.context, ResourcePath("Groups", self.resource_path)))

    @property
    def alerts(self):
        """Gets site alerts for this user."""
        return self.properties.get('Alerts',
                                   AlertCollection(self.context, ResourcePath("Alerts", self.resource_path)))

    @property
    def is_site_admin(self):
        """Gets a Boolean value that specifies whether the user is a site collection administrator."""
        return self.properties.get('isSiteAdmin', None)

    @property
    def user_id(self):
        """Gets the information of the user that contains the user's name identifier and the issuer of the
         user's name identifier."""
        return self.properties.get('UserId', UserIdInfo())

    @property
    def email(self):
        """
        Specifies the e-mail address of the user.
        It MUST NOT be NULL. Its length MUST be equal to or less than 255.

        :rtype: str or None
        """
        return self.properties.get('Email', None)

    def expire(self):
        qry = ServiceOperationQuery(self, "Expire")
        self.context.add_query(qry)
        return self

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "UserId": self.user_id,
            }
            default_value = property_mapping.get(name, None)
        return super(User, self).get_property(name, default_value)
