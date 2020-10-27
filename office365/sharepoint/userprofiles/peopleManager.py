from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.userprofiles.personProperties import PersonProperties
from office365.sharepoint.userprofiles.personPropertiesCollection import PersonPropertiesCollection
from office365.sharepoint.userprofiles.personalSiteCreationPriority import PersonalSiteCreationPriority


class PeopleManager(BaseEntity):
    """Provides methods for operations related to people."""

    def __init__(self, context):
        super().__init__(context, ResourcePath("SP.UserProfiles.PeopleManager"))

    def get_user_profile_properties(self, accountName):
        """
        :type accountName: str
        :return: dict
        """
        result = ClientResult(None)
        payload = {"accountName": accountName}
        qry = ServiceOperationQuery(self, "GetUserProfileProperties", payload, None, None, result)
        self.context.add_query(qry)
        return result

    def get_properties_for(self, accountName):
        """
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
        result = ClientResult(str)
        params = {"accountName": accountName,
                  "createSiteIfNotExists": createSiteIfNotExists,
                  "siteCreationPriority": siteCreationPriority}
        qry = ServiceOperationQuery(self, "GetDefaultDocumentLibrary", params, None, None, result)
        self.context.add_query(qry)
        return result

    def get_people_followed_by(self, accountName):
        """

        :type accountName: str
        :return: PersonPropertiesCollection
        """
        result = PersonPropertiesCollection(self.context)
        params = {"accountName": accountName}
        qry = ServiceOperationQuery(self, "GetPeopleFollowedBy", params, None, None, result)
        self.context.add_query(qry)
        return result
