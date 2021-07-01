from office365.runtime.client_runtime_context import ClientRuntimeContext


class ExcelService(ClientRuntimeContext):

    def __init__(self, context):
        """
        Excel Services REST API client
        https://docs.microsoft.com/en-us/sharepoint/dev/general-development/excel-services-rest-api
        """
        super(ExcelService, self).__init__()

    def authenticate_request(self, request):
        pass

    def service_root_url(self):
        return "{0}/_vti_bin/ExcelRest.aspx"

    def pending_request(self):
        pass

    def get_workbook(self, list_name, file_name):
        return self
