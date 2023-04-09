from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_user_credentials

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
result = ctx.search_setting.ping_admin_endpoint().execute_query()
if result.value:
    result = ctx.search_setting.export_search_reports(tenant_id="af6a80a4-8b4b-4879-88af-42ff8a545211",
                                                      report_type="ReportTopQueries").execute_query()
    print(result)
