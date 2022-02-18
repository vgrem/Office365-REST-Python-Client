from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.userprofiles.hash_tag import HashTagCollection
from office365.sharepoint.userprofiles.personalSiteCreationPriority import PersonalSiteCreationPriority
from office365.sharepoint.userprofiles.personProperties import PersonProperties
from office365.sharepoint.userprofiles.personPropertiesCollection import PersonPropertiesCollection


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
        result = ClientResult(self.context, PersonPropertiesCollection(self.context))
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "GetFollowersFor", params, None, None, result)
        self.context.add_query(qry)
        return result

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

    def get_user_profile_properties(self, account_name):
        """
        Gets the specified user profile properties for the specified user.

        :param str account_name: Account name of the specified user.
        """
        result = ClientResult(self.context)
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "GetUserProfileProperties", params, None, None, result)
        self.context.add_query(qry)
        return result

    def get_properties_for(self, account_name):
        """
        Gets user properties for the specified user.

        :type account_name: str
        :return: PersonProperties
        """
        result = PersonProperties(self.context)
        payload = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "GetPropertiesFor", payload, None, None, result)
        self.context.add_query(qry)
        return result

    def get_default_document_library(self, account_name, create_site_if_not_exists=False,
                                     site_creation_priority=PersonalSiteCreationPriority.Low):
        """

        :param str account_name:
        :param bool create_site_if_not_exists:
        :param int site_creation_priority:
        :return:
        """
        result = ClientResult(self.context)
        params = {"accountName": account_name,
                  "createSiteIfNotExists": create_site_if_not_exists,
                  "siteCreationPriority": site_creation_priority}
        qry = ServiceOperationQuery(self, "GetDefaultDocumentLibrary", params, None, None, result)
        self.context.add_query(qry)
        return result

    def get_people_followed_by(self, account_name):
        """
        The GetPeopleFollowedBy method returns a  list of PersonProperties objects for people who the specified user
        is following. This method can result in exceptions for conditions such as null arguments or if the specified
        user cannot be found.

        :param str account_name: Account name of the specified user.
        :return: PersonPropertiesCollection
        """
        result = PersonPropertiesCollection(self.context)
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "GetPeopleFollowedBy", params, None, None, result)
        self.context.add_query(qry)
        return result

    def get_my_followers(self):
        """
        This method returns a list of PersonProperties objects for the people who are following the current user.
        """
        return_type = PersonPropertiesCollection(self.context)
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
