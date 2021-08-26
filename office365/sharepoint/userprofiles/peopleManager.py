from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.userprofiles.personalSiteCreationPriority import PersonalSiteCreationPriority
from office365.sharepoint.userprofiles.personProperties import PersonProperties
from office365.sharepoint.userprofiles.personPropertiesCollection import PersonPropertiesCollection


class PeopleManager(BaseEntity):
    """Provides methods for operations related to people."""

    def __init__(self, context):
        super(PeopleManager, self).__init__(context, ResourcePath("SP.UserProfiles.PeopleManager"))

    def am_i_following(self, account_name):
        """
        Checks whether the current user is following the specified user.

        :param str account_name:
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

        :param str account_name:
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

        :param str account_name:
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

    def get_user_profile_properties(self, accountName):
        """
        Gets the specified user profile properties for the specified user.

        :type accountName: str
        :return: dict
        """
        result = ClientResult(self.context)
        payload = {"accountName": accountName}
        qry = ServiceOperationQuery(self, "GetUserProfileProperties", payload, None, None, result)
        self.context.add_query(qry)
        return result

    def get_properties_for(self, accountName):
        """
        Gets user properties for the specified user.

        :type accountName: str
        :return: PersonProperties
        """
        result = PersonProperties(self.context)
        payload = {"accountName": accountName}
        qry = ServiceOperationQuery(self, "GetPropertiesFor", payload, None, None, result)
        self.context.add_query(qry)
        return result

    def get_default_document_library(self, accountName, createSiteIfNotExists=False,
                                     siteCreationPriority=PersonalSiteCreationPriority.Low):
        """

        :param str accountName:
        :param bool createSiteIfNotExists:
        :param int siteCreationPriority:
        :return:
        """
        result = ClientResult(self.context)
        params = {"accountName": accountName,
                  "createSiteIfNotExists": createSiteIfNotExists,
                  "siteCreationPriority": siteCreationPriority}
        qry = ServiceOperationQuery(self, "GetDefaultDocumentLibrary", params, None, None, result)
        self.context.add_query(qry)
        return result

    def get_people_followed_by(self, account_name):
        """

        :type account_name: str
        :return: PersonPropertiesCollection
        """
        result = PersonPropertiesCollection(self.context)
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "GetPeopleFollowedBy", params, None, None, result)
        self.context.add_query(qry)
        return result

    def get_my_followers(self):
        """
        """
        return_type = PersonPropertiesCollection(self.context)
        qry = ServiceOperationQuery(self, "GetMyFollowers", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type
