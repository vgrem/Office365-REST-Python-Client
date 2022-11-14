from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.viva.app_configuration import AppConfiguration


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
        qry = ServiceOperationQuery(self, "VivaHomeConfiguration", None, None, None, return_type)
        self.context.add_query(qry)

        def _construct_request(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            request.method = HttpMethod.Get
        self.context.before_execute(_construct_request)
        return return_type

    @property
    def app_configuration(self):
        return self.properties.get("AppConfiguration",
                                   AppConfiguration(self.context, ResourcePath("AppConfiguration", self.resource_path)))

