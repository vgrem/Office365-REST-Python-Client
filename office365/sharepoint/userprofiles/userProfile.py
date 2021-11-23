from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.userprofiles.followedContent import FollowedContent


class UserProfile(BaseEntity):

    @property
    def public_url(self):
        """
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

    def create_personal_site_enque(self, isInteractive):
        """
        Enqueues creating a personal site for this user, which can be used to share documents, web pages,
            and other files.

        :type isInteractive: bool
        """
        payload = {"isInteractive": isInteractive}
        qry = ServiceOperationQuery(self, "CreatePersonalSiteEnque", None, payload, None, None)
        self.context.add_query(qry)
        return self
