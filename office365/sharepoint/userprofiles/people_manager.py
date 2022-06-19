from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.principal.user import User
from office365.sharepoint.userprofiles.hash_tag import HashTagCollection
from office365.sharepoint.userprofiles.personal_site_creation_priority import PersonalSiteCreationPriority
from office365.sharepoint.userprofiles.person_properties import PersonProperties


def _ensure_user(user_or_name, action):
    """
    :param str or User user_or_name: User or Login name of the specified user.
    :param (str) -> None action: Callback
    """
    if isinstance(user_or_name, User):
        def _user_loaded():
            action(user_or_name.login_name)
        user_or_name.ensure_property("LoginName", _user_loaded)
    else:
        action(user_or_name)


class PeopleManager(BaseEntity):
    """Provides methods for operations related to people."""

    def __init__(self, context):
        super(PeopleManager, self).__init__(context, ResourcePath("SP.UserProfiles.PeopleManager"))

    @staticmethod
    def get_trending_tags(context):
        """Gets a collection of the 20 (or fewer) most popular hash tags over the past week.
        The returned collection is sorted in descending order of frequency of use.

        :type context: office365.sharepoint.client_context.ClientContext
        """
        return_type = HashTagCollection(context)
        manager = PeopleManager(context)
        qry = ServiceOperationQuery(manager, "GetTrendingTags", None, None, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    def am_i_following(self, account_name):
        """
        Checks whether the current user is following the specified user.

        :param str account_name: Account name of the specified user.
        :return:
        """
        result = ClientResult(self.context)
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "AmIFollowing", params, None, None, result)
        self.context.add_query(qry)
        return result

    def get_followers_for(self, account_name):
        """
        Gets the people who are following the specified user.

        :param str account_name: Account name of the specified user.
        :return:
        """
        return_type = BaseEntityCollection(self.context, PersonProperties)
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "GetFollowersFor", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_user_information(self, account_name, site_id):
        """
        :param str account_name: Account name of the specified user.
        :param str site_id: Site Identifier.
        """
        return_type = ClientResult(self.context)
        params = {"accountName": account_name, "siteId": site_id}
        qry = ServiceOperationQuery(self, "GetSPUserInformation", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def follow(self, account_name):
        """
        Add the specified user to the current user's list of followed users.

        :param str account_name: Account name of the specified user.
        """
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "Follow", params, None, None, None)
        self.context.add_query(qry)
        return self

    def stop_following(self, account_name):
        """
        Remove the specified user from the current user's list of followed users.

        :param str account_name:
        """
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "StopFollowing", params, None, None, None)
        self.context.add_query(qry)
        return self

    def get_user_profile_properties(self, user_or_name):
        """
        Gets the specified user profile properties for the specified user.

        :param str or User user_or_name: User or Login name of the specified user.
        """
        return_type = ClientResult(self.context)

        def _user_resolved(account_name):
            params = {"accountName": account_name}
            qry = ServiceOperationQuery(self, "GetUserProfileProperties", params, None, None, return_type)
            self.context.add_query(qry)

        _ensure_user(user_or_name, _user_resolved)
        return return_type

    def get_properties_for(self, user_or_name):
        """
        Gets user properties for the specified user.

        :param str or User user_or_name: Specifies the User object or its login name.
        :return: PersonProperties
        """
        return_type = PersonProperties(self.context)

        def _get_properties_for_inner(account_name):
            params = {"accountName": account_name}
            qry = ServiceOperationQuery(self, "GetPropertiesFor", params, None, None, return_type)
            self.context.add_query(qry)

        _ensure_user(user_or_name, _get_properties_for_inner)
        return return_type

    def get_default_document_library(self, user_or_name, create_site_if_not_exists=False,
                                     site_creation_priority=PersonalSiteCreationPriority.Low):
        """
        Gets the OneDrive Document library path for a given user.

        :param str or User user_or_name user_or_name: The login name of the user whose OneDrive URL is required.
             For example, "i:0#.f|membership|admin@contoso.sharepoint.com”.
        :param bool create_site_if_not_exists: If this value is set to true and the site doesn't exist, the site will
            get created.
        :param int site_creation_priority: The priority for site creation. Type: PersonalSiteCreationPriority
        """
        return_type = ClientResult(self.context)

        def _get_default_document_library(account_name):
            params = {
                "accountName": account_name,
                "createSiteIfNotExists": create_site_if_not_exists,
                "siteCreationPriority": site_creation_priority
            }
            qry = ServiceOperationQuery(self, "GetDefaultDocumentLibrary", params, None, None, return_type)
            self.context.add_query(qry)

        _ensure_user(user_or_name, _get_default_document_library)
        return return_type

    def get_people_followed_by(self, account_name):
        """
        The GetPeopleFollowedBy method returns a  list of PersonProperties objects for people who the specified user
        is following. This method can result in exceptions for conditions such as null arguments or if the specified
        user cannot be found.

        :param str account_name: Account name of the specified user.
        :return: BaseEntityCollection
        """
        return_type = BaseEntityCollection(self.context, PersonProperties)
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "GetPeopleFollowedBy", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_my_followers(self):
        """
        This method returns a list of PersonProperties objects for the people who are following the current user.
        """
        return_type = BaseEntityCollection(self.context, PersonProperties)
        qry = ServiceOperationQuery(self, "GetMyFollowers", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def follow_tag(self, value):
        """
        The FollowTag method sets the current user to be following the specified tag.
        :param str value: Specifies the tag by its GUID.
        """

        qry = ServiceOperationQuery(self, "FollowTag", [value])
        self.context.add_query(qry)
        return self

    def hide_suggestion(self, account_name):
        """The HideSuggestion method adds the specified user to list of rejected suggestions.

        :param str account_name: Specifies the user by account name.
        """
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "HideSuggestion", params)
        self.context.add_query(qry)
        return self

    @property
    def entity_type_name(self):
        return "SP.UserProfiles.PeopleManager"
