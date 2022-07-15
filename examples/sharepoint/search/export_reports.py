from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.setting import SearchSetting
from tests import test_site_url, test_user_credentials

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
setting = SearchSetting(ctx)
result = setting.ping_admin_endpoint().execute_query()
if result.value:
    result = setting.export_search_reports(tenant_id="af6a80a4-8b4b-4879-88af-42ff8a545211",
                                           report_type="ReportTopQueries").execute_query()
    print(result)

