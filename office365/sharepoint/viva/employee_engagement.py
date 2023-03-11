from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.viva.app_configuration import AppConfiguration
from office365.sharepoint.viva.home import VivaHome


class EmployeeEngagement(BaseEntity):

    def __init__(self, context):
        super(EmployeeEngagement, self).__init__(context, ResourcePath("SP.EmployeeEngagement"))

    def dashboard_content(self, override_language_code=None):
        """
        :param str override_language_code:
        """
        return_type = ClientResult(self.context, str())
        payload = {"return return_type": override_language_code}
        qry = ServiceOperationQuery(self, "DashboardContent", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def viva_home_configuration(self):
        return_type = ClientResult(self.context, dict())
        qry = FunctionQuery(self, "VivaHomeConfiguration", None, return_type)
        self.context.add_query(qry)
        return return_type

    def viva_home(self):
        return_type = VivaHome(self.context)
        qry = ServiceOperationQuery(self, "VivaHome",  return_type=return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def app_configuration(self):
        return self.properties.get("AppConfiguration",
                                   AppConfiguration(self.context, ResourcePath("AppConfiguration", self.resource_path)))

